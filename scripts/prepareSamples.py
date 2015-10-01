#!/usr/bin/env python

import argparse

from QuickAnaHPC.setup import load_rc_libs, logger
from QuickAnaHPC.samples import scan_samples, split_samples, print_samples

def parse_args():
    """Parse command line arguments"""
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser('prepareSamples', formatter_class=formatter)
    add_arg = parser.add_argument
    add_arg('--output', default='samples',
            help='Output directory for SampleHandler')
    add_arg('--scanDir', default='$SCRATCH',
            help='Input dir to scan with SampleHandler for samples')
    add_arg('--samplePattern', action='append', default=[],
            help='Glob pattern for filtering samples in SampleHandler')
    add_arg('--splitEvents', type=int, help='Split samples by number of events')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    logger.info('Loading RootCore libraries')
    load_rc_libs(batch=True)
    sh = scan_samples(args.scanDir, args.samplePattern)
    if args.splitEvents is not None:
        sh = split_samples(sh, args.splitEvents)
    print_samples(sh)
    # Write out result
    sh.save(args.output)

if __name__ == '__main__':
    main()
