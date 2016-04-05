#!/usr/bin/env python

import os
import shutil
import argparse
import logging
from QuickAnaHPC.setup import load_rc_libs, logger
from QuickAnaHPC.samples import (scan_samples, split_samples,
                                 select_by_task, print_samples)

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
    add_arg('--scanDir', default='$GSCRATCH/xAOD',
            help='Input dir to scan with SampleHandler for samples')
    add_arg('--samplePattern', action='append', default=[],
            help='Glob pattern for filtering samples in SampleHandler')
    add_arg('--sampleHandler', help='Location of a saved SampleHandler ROOT file')
    add_arg('--splitSamples', type=int, help='Split samples by number of events')
    add_arg('--task', help='Task ID in format "ID:N", where N ' +
            'is the total number of tasks. If specified, the input samples ' +
            'will be split into N chunks and I will process chunk i=ID only.')
    add_arg('--maxEvents', type=int, help='Set max number of events per sample')
    add_arg('--writeXAOD', action='store_true',
            help='Activate output xAOD writing')
    add_arg('--driver', choices=['direct', 'pdsf', 'proof'], default='direct',
            help='Specify the EL driver to use')
    add_arg('--eventsPerWorker', type=int,
            help='Specify max number of events per worker in batch job')
    add_arg('--nProofWorkers', type=int,
            help='Specify number of workers for ProofDriver')
    add_arg('--opt', action='store_true',
            help='Enable optimized QuickAna scheduler')
    return parser.parse_args()

def load_samples(args):
    """
    Build a SampleHandler.
    Not all these options are compatible with each other.
    It might thus be better to split this up somehow.
    """
    from ROOT import SH
    if args.sampleHandler:
        sh = SH.SampleHandler()
        sh.load(args.sampleHandler)
    else:
        sh = scan_samples(args.scanDir, args.samplePattern)
    # Split samples by file if requested
    if args.splitSamples is not None:
        sh = split_samples(sh, args.splitSamples)
    # Choose samples according to task ID
    if args.task:
        task, numTasks = map(int, args.task.split(':'))
        sh = select_by_task(sh, task, numTasks)
    if args.eventsPerWorker:
        from ROOT import EL
        SH.scanNEvents(sh)
        sh.setMetaDouble(EL.Job.optEventsPerWorker, args.eventsPerWorker)
    return sh

def setup_driver(args):
    """Sets up the driver depending on the arguments"""
    from ROOT import EL
    if args.driver == 'direct':
        driver = EL.DirectDriver()
    elif args.driver == 'pdsf':
        driver = EL.SoGEDriver()
        driver.options().setString(EL.Job.optSubmitFlags, '-S /bin/bash')
        # TODO: make the IO configurable
        submit_opts = '-l gscratchio=1,h_vmem=6G'
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
    # Command line arguments
    args = parse_args()
    logger.info('Application begin')

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
    if len(sh) == 0:
        logger.info('Exiting early due to empty sample list')
        return

    # Configure the job
    job = EL.Job()
    job.sampleHandler(sh)
    # Perf stats
    jobOpts = job.options()
    jobOpts.setDouble(EL.Job.optXAODPerfStats, 1)
    jobOpts.setDouble(EL.Job.optCacheSize, 100*1024*1024)
    jobOpts.setDouble(EL.Job.optCacheLearnEntries, 10)
    if args.maxEvents:
        job.options().setInteger(job.optMaxEvents, args.maxEvents)

    # Setup the algorithm
    alg = AnalysisAlg()
    alg.electronDef = 'default'
    alg.muonDef = 'default'
    alg.tauDef = 'default'
    alg.jetDef = 'default'
    alg.metDef = 'default'
    alg.orDef = 'none'
    if args.noSysts:
        alg.doSystematics = False
    if args.opt:
        alg.schedulerDef = 'optimized'
    if args.writeXAOD:
        alg.writeXAOD = True
    job.algsAdd(alg)

    # Driver
    logger.info('Launching job with %s driver', args.driver)
    driver = setup_driver(args)
    driver.submit(job, args.jobDir)

    logger.info('Application finished')

if __name__ == '__main__':
    main()
