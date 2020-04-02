import argparse
import requests


from .common.config import load_config


class Client(object):
    def __init__(self, hostname, port):
        self._hostname = hostname
        self._port = port

    def execute(self, uri):
        base_url = 'http://{0}:{1}/'.format(self._hostname, self._port)
        r = requests.post(base_url + uri)
        if r.ok:
            return r.json()
        else:
            return '{0} - {1}'.format(r.status_code, r.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='simulation.cfg', help='The path to the configuration file.')
    parser.add_argument('uri', nargs='?', default='status', help='The uri path to hit (defaults to "/status").')
    args = parser.parse_args()

    config = load_config(args.config)
    client = Client(config['hostname'], config['port'])
    response = client.execute(args.uri)
    print(response)


if __name__ == '__main__':
    main()
