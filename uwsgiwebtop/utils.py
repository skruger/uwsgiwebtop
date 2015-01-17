
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

            results[url] = json.loads(data)
            results[url]['url'] = url
        except Exception as e:
            print "Exception {}: {}".format(e.__class__.__name__, e)

    for r in results:
        yield results[r]
