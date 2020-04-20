import unittest
import threading
import os

from .client import Client
from .server.server import Server
from requests.auth import HTTPBasicAuth


test_config = dict(
    hostname="localhost",
    port=8282,
    db="data/test.db",
)

class SimTest(unittest.TestCase):
    def do_single_request(self, path, method = "GET", data = []):
        """do_single_request

        Creates threads for both the server and client and executes a single request between the two.
        """
        self._client_response = None
        os.environ["TESTING"] = "true"

        httpd = Server(test_config)
        server_thread = threading.Thread(target=httpd.handle_request)
        server_thread.start()

        def client_thread_target(method, path, data):
            auth = HTTPBasicAuth("shatilov18@gmail.com", "password");
            client = Client(test_config["hostname"], test_config["port"], auth)
            self._client_response = client.execute(method, path, data)

        client_thread = threading.Thread(target=client_thread_target, args=(method, path, data))
        client_thread.start()

        server_thread.join()
        client_thread.join()

        return self._client_response

    def test_status(self):
        response = self.do_single_request("status")
        self.assertEqual(response, {"status": "OK"})

    def test_animals(self):
        response = self.do_single_request("animals")
        self.assertEqual(len(response["animals"]), 13)

    def test_animal_by_id(self):
        response = self.do_single_request("animal/1")
        self.assertEqual(
            response,
            {"animals": [{"id": 1, "name": "Bob", "species": "Llama"}]},
        )

    def test_404(self):
        response = self.do_single_request("some-missing-path")
        self.assertEqual(response[:3], "404")
