#!/usr/bin/env python

import os
import shutil
import argparse
import logging
logger = logging.getLogger('runQuickAnaHPC')

from XAODTestCodes.setup import load_rc_libs

def setup_logger(level=logging.INFO):
    """Sets up logging for the script"""
    logger.setLevel(level)
    ch = logging.StreamHandler()
    log_string = '%(name)s   %(levelname)s   %(message)s'
    formatter = logging.Formatter(log_string)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def parse_args():
    """Parse command line arguments"""
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser('QuickAnaHPC', formatter_class=formatter)
    add_arg = parser.add_argument
    add_arg('--noSysts', action='store_true', help='Disable systematics')
    add_arg('--jobDir', default='jobDir',
            help='Output directory for EventLoop')
    add_arg('--overwrite', action='store_true',
            help='Overwrite jobDir if it exists')
    add_arg('--scanDir', default='$SCRATCH',
            help='Input dir to scan with SampleHandler for samples')
    add_arg('--samplePattern', default='*',
            help='Glob pattern for filtering samples in SampleHandler')
    add_arg('--maxEvents', help='Set max number of events per sample')
    add_arg('--driver', choices=['direct', 'pdsf', 'proof'], default='direct',
            help='Specify the EL driver to use')
    add_arg('--eventsPerWorker', type=int,
            help='Specify max number of events per worker in batch job')
    add_arg('--nProofWorkers', type=int,
            help='Specify number of workers for ProofDriver')
    add_arg('--opt', action='store_true',
            help='Enable optimized QuickAna scheduler')
    # Options to add:
    # - pre-built SampleHandler directory to load from
    return parser.parse_args()

def load_samples(args):
    """Build a SampleHandler"""
    from ROOT import SH
    sh = SH.SampleHandler()
    sh.setMetaString('nc_tree', 'CollectionTree')
    scanDir = os.path.expandvars(args.scanDir)
    SH.ScanDir().samplePattern(args.samplePattern).scan(sh, scanDir)
    if args.eventsPerWorker:
        from ROOT import EL
        SH.scanNEvents(sh)
        sh.setMetaDouble(EL.Job.optEventsPerWorker, args.eventsPerWorker)
    return sh

def print_samples(sh):
    """Compactly print out contents of a SampleHandler"""
    logger.info('Number of samples: %i', len(sh))
    for s in sh:
        logger.info('Sample: %s', s.name())
        logger.info('  Number of files:  %i', s.numFiles())
        logger.info('  Number of events: %i', s.getNumEntries())

def setup_driver(args):
    """Sets up the driver depending on the arguments"""
    from ROOT import EL
    if args.driver == 'direct':
        driver = EL.DirectDriver()
    elif args.driver == 'pdsf':
        driver = EL.SoGEDriver()
        driver.options().setString(EL.Job.optSubmitFlags, '-S /bin/bash')
        # TODO: make the IO configurable
        submit_opts = '-l gscratchio=1,h_vmem=8G'
        driver.options().setString('nc_EventLoop_SubmitFlags', submit_opts)
        driver.shellInit = 'shopt -s expand_aliases\n'
    elif args.driver == 'proof':
        driver = EL.ProofDriver()
        if args.nProofWorkers is not None:
            driver.numWorkers = args.nProofWorkers
    else:
        raise Exception('Unsupported driver type: ' + args.driver)
    return driver

def main():
    """Main executable function"""
    setup_logger()
    logger.info('Application begin')

    # Command line arguments
    args = parse_args()

    # Delete jobDir if requested
    if args.overwrite and os.path.exists(args.jobDir):
        shutil.rmtree(args.jobDir)

    # RootCore libraries
    logger.info('Loading RootCore libraries')
    load_rc_libs(batch=True)
    from ROOT import EL, AnalysisAlg

    # Setup samples
    logger.info('Loading samples')
    sh = load_samples(args)
    print_samples(sh)

    # Configure the job
    job = EL.Job()
    job.sampleHandler(sh)
    if args.maxEvents:
        job.options().setInteger(job.optMaxEvents, int(args.maxEvents))

    # Setup the algorithm
    alg = AnalysisAlg()
    alg.electronDef = 'default'
    alg.muonDef = 'default'
    alg.tauDef = 'default'
    alg.jetDef = 'default'
    alg.metDef = 'default'
    alg.orDef = 'default'
    if args.noSysts:
        alg.doSystematics = False
    if args.opt:
        alg.schedulerDef = 'optimized'
    job.algsAdd(alg)

    # Driver
    logger.info('Launching job with %s driver', args.driver)
    driver = setup_driver(args)
    driver.submit(job, args.jobDir)

    logger.info('Application finished')

if __name__ == '__main__':
    main()
