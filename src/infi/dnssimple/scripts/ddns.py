"""ddns v{0}
Usage:
   ddns update <domain> <token> [<hostname> [<address>]]

"""

import sys
import json
import socket
import docopt
import requests
import infi.traceback


def get_hostname():
    return socket.gethostname().split('.')[0]


def get_external_ipv4_address():
    return requests.get("http://icanhazip.com/").text.strip()


def update_dns(domain, token, name, ipv4_adress):
    base_url = "https://api.dnsimple.com/v1/domains/{0}/records".format(domain)
    headers = {"X-DNSimple-Domain-Token": token, "Accept": "application/json",  "Content-Type": "application/json"}

    records = {item['record']['name']: item['record'] for
               item in requests.get(base_url, headers=headers).json() if
               'record' in item and 'name' in item['record']}

    if name in records:
        update_url = "{0}/{1}".format(base_url, records[name]['id'])
        data = {"record": {"content": ipv4_adress, "name": name}}
        result = requests.put(update_url, headers=headers, data=json.dumps(data))
    else:
        data = {"record": {"content": ipv4_adress, "name": name, "record_type": "A", "ttl": 60, "prio": 10}}
        result = requests.post(base_url, headers=headers, data=json.dumps(data))

    result.raise_for_status()
    return result.json()


@infi.traceback.pretty_traceback_and_exit_decorator
def main(argv=sys.argv[1:]):
    from infi.dnssimple.__version__ import __version__
    arguments = docopt.docopt(__doc__.format(__version__), version=__version__, argv=argv)
    print update_dns(arguments['<domain>'], arguments['<token>'],
                     arguments.get('<hostname>') or get_hostname(),
                     arguments.get('<address>') or get_external_ipv4_address())
