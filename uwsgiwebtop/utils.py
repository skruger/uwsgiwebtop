
import os
import socket
import json
import time

from collections import OrderedDict


class WorkerRecord:
    def __init__(self, worker):
        self.worker = worker
        self.request = worker['requests']
        self.seen_time = time.time()

class StuckWorkerDetector:
    def __init__(self):
        self.busy_workers = dict()

    def _busy_workers_key(self, url, worker):
        return "{}_{}".format(url, worker['id'])

    def check_busy_time(self, url, worker):
        new_worker_rec = WorkerRecord(worker)
        worker_key = self._busy_workers_key(url, worker)
        if worker['status'] == 'busy':
            # Get existing or new busy worker record
            bw = self.busy_workers.get(worker_key, new_worker_rec)
            # Replace the old busy worker record if on a different
            # serially incrementing request
            if bw.request != new_worker_rec.request:
                bw = new_worker_rec
            self.busy_workers[worker_key] = bw
            # Return number of seconds worker has been seen busy on this request
            return int(time.time() - bw.seen_time)
        else:
            if worker_key in self.busy_workers:
                del self.busy_workers[worker_key]
            return 0


stuck_worker_detector = StuckWorkerDetector()

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
                w['busy_time'] = stuck_worker_detector.check_busy_time(url, w)
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
