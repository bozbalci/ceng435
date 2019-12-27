import json
import sys
from argparse import ArgumentParser

from .destination import Destination
from .router import Router
from .source import Source

parser = ArgumentParser(description='CENG435 Term Project - Part II - Experiment Scripts')
parser.add_argument('--router', action='store_true', dest='router_mode',
                    help='only forward packets from/to s and d')
parser.add_argument('--source', action='store_true', dest='source_mode',
                    help='send an input file to the destination node')
parser.add_argument('--destination', action='store_true', dest='destination_mode',
                    help='receive an input file from the source node')
parser.add_argument('file', nargs='?', default=None)
parser.add_argument('-E', dest='experiment_id', nargs='?', default=1)
parser.add_argument('-c', dest='count', nargs='?', default=1,
                    help='run the experiment N times', metavar='N', type=int)

if __name__ == '__main__':
    args = parser.parse_args()

    if args.router_mode:
        router = Router()
        router.run()
        sys.exit(0)
    elif args.source_mode:
        if not args.file:
            raise Exception("an input file path must be given to the script when running as source")
        source = Source(args.file, experiment_id=args.experiment_id)
        results = source.run(count=args.count)
        with open('stats.json', 'r') as infile:
            old_results = json.load(infile)
        with open('stats.json', 'w') as outfile:
            json.dump(old_results + results, outfile)
        sys.exit(0)
    elif args.destination_mode:
        if not args.file:
            raise Exception("an output file path must be given to the script when running as source")
        destination = Destination(args.file)
        destination.run(count=args.count)
        sys.exit(0)
