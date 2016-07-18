"""ddns v{0}
Usage:
   ddns update <domain> <token> [<hostname> [<address>]]
   ddns add <domain> <token> <name> <type> <content>
   ddns delete <domain> <token> <name> <type> <content>
   ddns dump <domain> <token>
"""

import sys
import json
import socket
import docopt
import requests


def silence_requests_warning():
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()


def get_hostname():
    return socket.gethostname().split('.')[0]


def get_external_ipv4_address():
    return requests.get("http://icanhazip.com/").text.strip()


def update_dns(domain, token, name, content, record_type="A", ttl=60, prio=10):
    base_url = "https://api.dnsimple.com/v1/domains/{0}/records".format(domain)
    headers = {"X-DNSimple-Domain-Token": token, "Accept": "application/json",  "Content-Type": "application/json"}

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    records = {item['record']['name']: item['record'] for
               item in response.json() if 'record' in item and 'name' in item['record']}

    if name and name in records:
        update_url = "{0}/{1}".format(base_url, records[name]['id'])
        data = {"record": {"content": content, "name": name}}
        result = requests.put(update_url, headers=headers, data=json.dumps(data))
    else:
        data = {"record": {"content": content, "name": name, "record_type": record_type, "ttl": ttl, "prio": prio}}
        result = requests.post(base_url, headers=headers, data=json.dumps(data))

    result.raise_for_status()
    return result.json()


def delete_dns(domain, token, name, content, record_type="A"):
    base_url = "https://api.dnsimple.com/v1/domains/{0}/records".format(domain)
    headers = {"X-DNSimple-Domain-Token": token, "Accept": "application/json",  "Content-Type": "application/json"}

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    [record] = [item['record'] for item in response.json() if
                'record' in item and item['record']['name'] == name and
                item['record']['content'] == content and item['record']['record_type'] == record_type]

    delete_url = "{0}/{1}".format(base_url, record['id'])
    result = requests.delete(delete_url, headers=headers)

    result.raise_for_status()
    return result.json()


def dump_dns(domain, token):
    from json import dumps
    base_url = "https://api.dnsimple.com/v1/domains/{0}/records".format(domain)
    headers = {"X-DNSimple-Domain-Token": token, "Accept": "application/json",  "Content-Type": "application/json"}

    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    return dumps(response.json(), indent=4)


def main(argv=sys.argv[1:]):
    from infi.dnssimple.__version__ import __version__
    from infi.traceback import pretty_traceback_and_exit_decorator
    arguments = docopt.docopt(__doc__.format(__version__), version=__version__, argv=argv)
    silence_requests_warning()
    if arguments['update']:
        name = arguments.get('<hostname>') or get_hostname()
        address = arguments.get('<address>') or get_external_ipv4_address()
        func = pretty_traceback_and_exit_decorator(update_dns)
        print func(arguments['<domain>'], arguments['<token>'], name, address)
    elif arguments['add']:
        func = pretty_traceback_and_exit_decorator(update_dns)
        args = arguments['<domain>'], arguments['<token>'], arguments['<name>'], arguments['<content>'], arguments['<type>']
        print func(*args)
    elif arguments['delete']:
        func = pretty_traceback_and_exit_decorator(delete_dns)
        args = arguments['<domain>'], arguments['<token>'], arguments['<name>'], arguments['<content>'], arguments['<type>']
        print func(*args)
    elif arguments['dump']:
        func = pretty_traceback_and_exit_decorator(dump_dns)
        args = arguments['<domain>'], arguments['<token>']
        print func(*args)
