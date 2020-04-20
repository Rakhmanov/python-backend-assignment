import argparse
import requests
import os
import datetime
import time
import pickle
import json
from  urllib.parse import parse_qs, urlparse

from requests.auth import HTTPBasicAuth, AuthBase
from .common.config import load_config

class Token():
    """Token
    
    Used to create local file for the client where session is stored between requests.
    Ideally it would be moved in to its own file and imported.
    """
    filename = ".session"

    @classmethod
    def get(cls):
        read_data = None
        if cls.exist():
            with open(cls.filename, "rb") as f:
                read_data = f.read()
            return read_data

    @classmethod
    def create(cls, token):
        with open(cls.filename, "wb") as f:
            f.write(token)

    @classmethod
    def exist(cls):
        return os.path.isfile(cls.filename) and time.time() - os.stat(cls.filename).st_mtime <= 30 * 60

class Client(object):
    def __init__(self, hostname, port, auth: AuthBase):
        protocol = "https"
        if os.environ.get('TESTING') == "true":
            protocol = "http"
        self._base_url = "{0}://{1}:{2}/".format(protocol, hostname, port)
        self._session = requests.Session()
        self._session.auth = auth
        self._session.verify = "certs/rootCA.pem"
        self._session.cert = ("certs/client.localhost.crt", "certs/client.localhost.key")

    def execute(self, method, uri, data):
        r = self._session.request(method, self._base_url + uri, json=data)
        server_session = r.cookies.get("session")
        if r.ok:
            return r.json()
        else:
            print(r)
            return "{0} - {1}".format(r.status_code, r.text)

def main():
    """main
    
    This grew a little bit, please refer to help or getting started for command help.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="simulation.cfg", help="The path to the configuration file.")
    parser.add_argument("-u", "--user", help="User to be used to authenticate to the server.")
    parser.add_argument("-p", "--password", help="Password to be used to authenticate to the server.")
    parser.add_argument("-d", "--data", nargs="*", help="To create a new record provide name and species to save. Eg \"--save Tom Cat\"")
    parser.add_argument("-m", "--method",  default="GET", choices=("GET", "POST"), help="Request's method.")
    parser.add_argument("uri", nargs="?", default="status", help="The uri path to hit (defaults to \"/status\").")

    args = parser.parse_args()
    config = load_config(args.config)
    client: Client = None

    """When credentials are not provided try to load session from disk.
    """
    if not args.user and not args.password:
        pickled_client = Token.get()
        if pickled_client:
            client = pickle.loads(pickled_client)
        else:
            return print ("Please authenticate by providing user and password to the client. Eg `-u user -p password`")

    data = [];
    if args.data:
        args.method = "POST";
        for value in args.data:
            data.append(parse_qs(value))

    if not client:
        auth = HTTPBasicAuth(args.user, args.password);
        client = Client("localhost", config["port"], auth)
    try: 
        response = client.execute(args.method, args.uri, data)
    except requests.exceptions.ConnectionError as e:
        return print ("Connection error. Please make sure server is running. " + str(e))

    """Sanitize object of credentials,
        then save session cookies and other Client parameters.
    """
    client._session.auth = None
    Token.create(pickle.dumps(client))

    print(response)

if __name__ == "__main__":
    main()
