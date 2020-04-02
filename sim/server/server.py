import argparse
import logging
import json

from http.server import HTTPServer, BaseHTTPRequestHandler

from . import db
from ..common.config import load_config


class BaseJSONHandler(BaseHTTPRequestHandler):
    """BaseJSONHandler

    This handler class manages incoming POST requests and returns JSON-formatted dictionaries.
    Subclasses are intended to implement the path handlers and associated execution methods.
    """
    def do_POST(self):
        try:
            handler = self.get_handler_for_path(self.path)
            if handler is None:
                self.send_error(404)
            else:
                response_object = handler()
                self._send_json_response(response_object)
        except Exception:
            logging.exception('Uncaught exception')
            self.send_error(500)

    def get_handler_for_path(self, path):
        """get_handler_for_path

        Should be implemented by subclasses.
        Returns:
            Callable if found, None otherwise.
        """
        raise NotImplementedError()

    def _send_json_response(self, json_object):
        response_content = json.dumps(json_object).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response_content))
        self.end_headers()
        self.wfile.write(response_content)


class RequestHandler(BaseJSONHandler):
    """RequestHandler

    Implements path handlers for the server.
    """
    def get_handler_for_path(self, path):
        handlers = {
            '/status': self._handle_status_request,
            '/animals': self._handle_animals_request,
        }
        return handlers.get(path)

    def _handle_status_request(self):
        return {'status': 'ok'}

    def _handle_animals_request(self):
        session = self.server.database.create_session()
        try:
            animals = session.query(db.Animal).all()
            return {'animals': [a.as_dict() for a in animals]}
        finally:
            session.close()


class Server(HTTPServer):
    def __init__(self, config):
        super().__init__(
            (config['hostname'], config['port']),
            RequestHandler,
        )
        self.config = config
        self.database = db.Database(config)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Simulation server starting...')
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='simulation.cfg')
    args = parser.parse_args()

    httpd = Server(load_config(args.config))
    httpd.serve_forever()


if __name__ == '__main__':
    main()
