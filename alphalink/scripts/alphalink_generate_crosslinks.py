"""
Script to convert crosslink tables to pickled dictionaries.

example:
    $ alphalink2-crosslinks --csv crosslinks.csv --out crosslinks.pkl

The script converts 1-based crosslinking information to 0-based
dictionaries in pickle format.

from_pos chain_a to_pos chain_b false discovery rate
5 A 78 B 0.2
10 A 78 B 0.2
16 A 99 B 0.2
16 A 102 B 0.2
17 A 56 B 0.2
"""
import gzip
import pickle
from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

import numpy as np


def crosslink_parser():
    parser = ArgumentParser(description=__doc__, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--csv', help='CSV with contacts: i chain1 j chain2 FDR', required=True)
    parser.add_argument('--output', help='Output pickle for crosslink constraints.', required=True)

    return parser


def main(args=None):
    if not args:
        args = crosslink_parser().parse_args()
    import logging
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
                        handlers=[logging.StreamHandler()])

    logging.info(f"Loading CSV File: {args.csv}")
    links = np.loadtxt(args.csv, dtype=str)

    if len(links.shape) == 1:
        links = np.array([links])

    crosslinks = {}

    for i, chain1, j, chain2, fdr in links:
        i = int(i)
        j = int(j)
        fdr = float(fdr)
        if chain1 not in crosslinks:
            crosslinks[chain1] = {}
        if chain2 not in crosslinks[chain1]:
            crosslinks[chain1][chain2] = []

        crosslinks[chain1][chain2].append((i - 1, j - 1, fdr))

    logging.info(f"Number of chains: {len(crosslinks)}")
    logging.info(f"Saving pickle to: {args.output}")
    pickle.dump(crosslinks, gzip.open(args.output, 'wb'))


if __name__ == "__main__":
    main()
