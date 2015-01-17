import os
import sys
import getopt

from uwsgiwebtop import server

USAGE = """
-h
    Show this help
-p <port>
    Set listen port (default: 8088)
-s <stats1>,<stats2>,<stats3> | --stats <stats1>,<stats2>,<stats3>
    Set list of servers to collect stats from (required)
"""

def main():
    port = 8088
    stats = None
    opts, args = getopt.getopt(sys.argv[1:], 'hp:s:', ['stats='])
    for k, v in opts:
        if k == '-p':
            port = int(v)
        elif k == '--stats' or k == '-s':
            stats = v
        if k == '-h':
            print USAGE
            return
    if not stats:
        print "{}\nRequired option not supplied.".format(USAGE)
        return
    os.environ["UWSGIWEBTOP_STATS_URLS"] = stats
    server.run_server(port=port)

if __name__ == '__main__':
    main()
