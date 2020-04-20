import argparse
import json
import logging
import os
import ssl
import urllib.parse

from collections.abc import Iterable
from itertools import chain
from sqlalchemy import or_
from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler 
from hmac import compare_digest

from . import db
from . import auth
from . import router
from ..common.config import load_config
from sqlalchemy.exc import InvalidRequestError

""" Ideally I would completely build this classes out to read and send data, 
     making it the layer of obstraction on top of standard BaseHTTPRequestHandler and http.server"s methods.

    The following classes I would move to the separate file and import. 
    Also In this code I did not focus on public/private method hierarchy. 
    I have left it and many other things out, due to time constraint when dealing with oop design,
     and focusing on solving tasks at hand.
"""
class Response:
    def __init__(self):
        self.headers = []

    def add_header(self, key, value):
        self.headers.append((key, value))

    def add_cookie(self, key, value):
        cookie = SimpleCookie()
        cookie[key] = value
        self.headers.append(("Set-Cookie", cookie.output(header="", sep="")))
class Request:
    def __init__(self):
        self.body = None
        self.cookies = None
        self.ip = None
        self.path = None
        self.path_parts = None
class Data:
    def __init__(self):
        self.db_session = None
        self.user = None
class CompanyStore:
    def __init__(self):
        self.data = Data()
        self.request = Request()
        self.response = Response()

class BaseJSONHandler(BaseHTTPRequestHandler):
    """BaseJSONHandler

    This handler class manages incoming POST requests and returns JSON-formatted dictionaries.
    Subclasses are intended to implement the path handlers and associated execution methods.
    """
    def __init__(self, request, client_address, server):
        """ Give each connection db session """
        self.company = CompanyStore()
        self.company.data.db_session = server.database.create_session();
        super().__init__(request, client_address, server)

    def authorize(self):
        """authorize
        
        Checks if user already has valid session, or tries to authorise with credentials.
        On successful auth creates session and sends cookies to the client.
        @returns db.User 
        """
        session_id = self.company.request.cookies.get("session")
        if session_id:
            session = self.company.data.db_session.query(db.Session).get(session_id)
            if session and not session.is_expired() and session.user:
                return session.user

        if not self.headers.get("authorization"):
            raise ConnectionRefusedError()

        credentials = auth.DecodeBase64(self.headers.get("authorization"))
        email = credentials[0].strip()
        password = credentials[1].strip()
        user = self.company.data.db_session.query(db.User).filter_by(email=email).first()

        if not user:
            raise ConnectionRefusedError()

        result = auth.VerifyPassword(user.password, password)
        if not result:
            raise ConnectionRefusedError()
        
        user.sessions = [db.Session(client_ip = self.company.request.ip)]

        self.company.data.db_session.commit()
        self.company.response.add_cookie("session", user.sessions[0].id)
        return user

    def get_request_body(self):
        """get_request_body
        
        Parsing json request body
        """
        if self.headers.get("content-type") == "application/json":
            body_length = self.headers.get("content-length")
            request = self.rfile.read(int(body_length))
            request_json = json.loads(request)
            return request_json

        if self.headers.get("content-type") == "application/x-www-form-urlencoded":
            body_length = self.headers.get("content-length")
            request = self.rfile.read(int(body_length)).decode("utf-8")
            request_parsed = urllib.parse.parse_qs(request, encoding="utf-8")
            return request_parsed
        return

    def get_cookies(self):
        """ get_cookies

        Dictionaries from request cookies.
        """
        cookies = filter(None, self.headers.get_all("cookie", []))
        cookie_dict = {}
        if cookies:
            for c in cookies:
                halves = c.split("=")
                cookie_dict[halves[0]] = halves[1]
    
        return cookie_dict

    def do_POST(self):
        self.process_request()

    def do_GET(self):
        self.process_request()

    def log(self):
        """log

        Tracking Access
        """
        body = self.company.request.body

        if not body and body is not None:
            body = bytes(body)

        if body:
            body = json.dumps(body).encode("utf-8")

        self.company.data.user.access_logs.append(db.AccessLog(client_ip = self.company.request.ip, 
                                                             resource=self.company.request.path, 
                                                             method=self.company.request.method, 
                                                             body=body))

        self.company.data.db_session.commit()

    def process_request(self):
        """process_request

        Method to handle all request fulfilment.
        Ideally if I was going to have it being used, 
        I would create router that does real path matching using regex rules, and create middleware flow.
        This method would also be broken down to cleaner methods based on responsobilities.
        """
        try:
            self.company.request.cookies = self.get_cookies()
            self.company.request.body = self.get_request_body()
            self.company.request.ip = self.address_string()
            self.company.request.method = self.command
            self.company.request.path = self.path
            self.company.data.user = self.authorize()
            self.log()

            route = self.routes(self.command, self.company.request.path)
            if route is None:
                return self.send_error(404)

            response_content = json.dumps(route(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            for header in self.company.response.headers:
                self.send_header(header[0], header[1]);
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(response_content))
            self.end_headers()
            self.wfile.write(response_content)

        except ConnectionRefusedError:
            self.send_response(401, "Unauthorized")
            self.send_header("WWW-Authenticate", "Basic realm=\"Access to the staging site\", charset=\"UTF-8\"")
            self.end_headers()
        except InvalidRequestError:
            self.send_error(422)
        except Exception as e:
            logging.error(e)
            self.send_error(500)


        self.company.data.db_session.close()

    def routes(self, method, path):
        """handler_for_path

        Should be implemented by subclasses.
        Returns:
            Callable if found, None otherwise.
        """
        raise NotImplementedError()

    def sendModel(self, key, result):
        """send

        Helper method to format json from the model.
        """
        response = []
        if result is None:
            return { key: result }

        if isinstance(result, Iterable):
            for r in result:
                response.append(r.as_dict())
        else:
            response.append(result.as_dict())

        return { key: response }

class RequestHandler(BaseJSONHandler):
    """RequestHandler

    Implements path handlers for the server.
    """

    def routes(self, method, path):
        """ In a perfect world, I would make Middleware type a class and handles as routes.
            But then I will be reinventing Flask.
        """

        handlers = {
            "POST": [
                ("/animal", self._handle_post_animal),
                ("/user", self._handle_post_user),

            ],
            "GET": [
                ("/", self._handle_get_status),
                ("/animals", self._handle_get_all_animals),
                ("/animals/species/{species}", self._handle_get_animals_by_species),
                ("/animal/{animal_id}", self._handle_get_animal_by_id),
                ("/status", self._handle_get_status),
                ("/users", self._handle_get_users),
            ]
        }
        """
        This is not performat way of routing each request.
        Ideally I would move the initialisation to the Server instance, 
         this way scanning for variables in names and regexing routes would not be done each request.
        """
        router_instance = router.Router(handlers)
        return router_instance.match(method, path)

    def _handle_get_users(self):
        users = self.company.data.db_session.query(db.User).all()
        return {"users": [a.as_dict() for a in users]}

    def _handle_get_status(self):
        return {"status": "OK"}

    def _handle_get_animal_by_id(self, animal_id):
        def _get_animals_by_id(animal_id):
            return self.company.data.db_session.query(db.Animal)\
                .filter(or_(db.Animal.author_id==None, db.Animal.author_id==self.company.data.user.id))\
                .filter(db.Animal.id==animal_id)\
                .first()
        result = None

        try:
            result = _get_animals_by_id(animal_id)
        except:
            raise InvalidRequestError

        return self.sendModel("animals", result)

    def _handle_get_animals_by_species(self, species):
        def _get_animals_by_species(species):
            return self.company.data.db_session.query(db.Animal).filter(db.Animal.species==species.capitalize())\
                .filter(or_(db.Animal.author_id==None, db.Animal.author_id==self.company.data.user.id))\
                .all()

        try:
            result = _get_animals_by_species(species)
        except:
            raise InvalidRequestError
        
        return self.sendModel("animals", result)

    def _handle_get_all_animals(self):
        def _get_all_animals():
            return self.company.data.db_session.query(db.Animal)\
                .filter(or_(db.Animal.author_id==None, db.Animal.author_id==self.company.data.user.id))\
                .all()

        return self.sendModel("animals", _get_all_animals())

    def _handle_post_animal(self):
        data_name = None
        data_species = None
        data = None

        """ If we get array of object just take first one 
        Addition of  multiple animals is not yet supported.
        """
        data = self.company.request.body
        
        if not isinstance(data, dict):
            data = self.company.request.body[0]

        try:
            if isinstance(data["name"], Iterable):
             data_name = data["name"][0]

            if isinstance(data["species"], Iterable):
                data_species = data["species"][0]
        except KeyError as key:
            return "Please provide parameters (name, species) for adding an animal"
                    

        """ If the values are arrays just take first one
        """

        animal = db.Animal(name=data_name, species=data_species)
        self.company.data.user.animals.append(animal)
        try:
            self.company.data.db_session.commit()
        except InvalidRequestError:
            raise InvalidRequestError

        return {"status": "success", "data": { "id": animal.id} }

    def _handle_post_user(self):
        data_name = None
        data_email = None
        data_last_name = None
        data_password = None
        data = self.company.request.body
        
        if not isinstance(data, dict):
            data = self.company.request.body[0]

        """ This section is very unpleasant but it has to deal with values as lits
        Ideally I would make helper function, or just flatten all input with a single value.
        """
        try:
            if isinstance(data["name"], Iterable):
                data_name = data["name"][0]
            if isinstance(data["email"], Iterable):
                data_email = data["email"][0]
            if isinstance(data["last_name"], Iterable):
                data_last_name = data["last_name"][0]
            if isinstance(data["password"], Iterable):
                data_password = data["password"][0]

        except KeyError as key:
            return "Please provide parameters (name, last_name, password) for adding an animal"

        user = self.company.data.db_session.query(db.User).filter_by(email=data_email).first() 
        if user:
            return "This user already exist."

        data_password = auth.HashPassword(data_password);

        user = db.User(name=data_name, last_name=data_last_name, email=data_email, password=data_password)
        self.company.data.db_session.add(user)

        try:
            self.company.data.db_session.commit()
        except InvalidRequestError:
            raise InvalidRequestError

        return {"status": "success", "data": { "id": user.id} }

class Server(HTTPServer):
    def __init__(self, config):
        super().__init__(
            ("0.0.0.0", config["port"]),
            RequestHandler,
        )
        self.config = config
        self.database = db.Database(config)

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Simulation server starting...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="simulation.cfg")
    args = parser.parse_args()
    httpd = Server(load_config(args.config))

    if not os.environ.get('TESTING'):
        httpd.socket = ssl.wrap_socket(httpd.socket, 
            keyfile="certs/server.localhost.key", 
            ca_certs="certs/rootCA.pem",
            certfile="certs/server.localhost.crt", server_side=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()