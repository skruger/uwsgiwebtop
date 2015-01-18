
import os
import socket
import json

from collections import OrderedDict

def collect_stats():
    results = OrderedDict()
    stats_urls = os.environ.get("UWSGIWEBTOP_STATS_URLS", "").split(',')
    for url in stats_urls:
        try:
            data = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            host, port = url.split(':')
            s.connect((host, int(port)))
            while True:
                buff = s.recv(4096)
                if not buff:
                    break
                data += buff

            stats = json.loads(data)
            for w in stats['workers']:
                for c in w['cores']:
                    c['vars_dict'] = parse_core_vars(c['vars'])

            results[url] = stats
            results[url]['url'] = url
        except Exception as e:
            print "Exception {}: {} while processing {}".format(e.__class__.__name__, e, url)

    for r in results:
        yield results[r]


def parse_core_vars(vars):
    result = dict()
    for v in vars:
        try:
            k, val = v.split('=', 1)
            result[k] = val
        except ValueError:
            # Ignore anything that doesn't parse with an '='
            pass
    return result
