import os
from setup import logger

def scan_samples(scanDir, samplePatterns = []):
    """Scan a filesystem and build a SampleHandler"""
    from ROOT import SH
    sh = SH.SampleHandler()
    sh.setMetaString('nc_tree', 'CollectionTree')
    scanDir = os.path.expandvars(scanDir)
    if len(samplePatterns) > 0:
        patterns = ['*'+p+'*' for p in samplePatterns]
        if len(patterns) == 0: patterns = ['*']
        for pattern in patterns:
            SH.ScanDir().samplePattern(pattern).scan(sh, scanDir)
    else:
        SH.ScanDir().scan(sh, scanDir)
    return sh

def split_samples(sh, num_events=150000):
    """
    Split a sample handler's samples into smaller samples of size num_events.
    This function does not split individual files.
    """
    from ROOT import SH
    splitSH = SH.SampleHandler()
    SH.scanNEvents(sh)
    for sample in sh:
        splitSH.add(SH.splitSample(sample, num_events))
    return splitSH

def _split_samples_worker(sample, num_events):
    """Worker process function for split_samples_mp"""
    from ROOT import SH
    SH.scanNEvents(sample)
    return SH.splitSample(sample, num_events)

def split_samples_mp(sh, num_events=150000, num_workers=8):
    """
    Same as split_samples function except uses a pool of process workers to
    scan and split samples.
    """
    import multiprocessing as mp
    from functools import partial
    from ROOT import SH

    # Need to set the num_events parameter ahead of time for pool.map
    worker = partial(_split_samples_worker, num_events=num_events)

    # Start the worker pool
    pool = mp.Pool(processes=num_workers)
    samples = [s for s in sh]
    samples = pool.map(worker, samples)

    # Combine results into new SampleHandler
    splitSH = SH.SampleHandler()
    for s in samples:
        splitSH.add(s)
    return splitSH

def select_by_task(sh, task_id, num_tasks):
    """
    Returns a new SampleHandler object with the fractional subset of samples
    for one task according to its index in the task list.
    """
    from ROOT import SH
    # Create new SampleHandler for this task
    taskSH = SH.SampleHandler()
    if task_id < num_tasks:
        for i in xrange(task_id, len(sh), num_tasks):
            taskSH.add(sh[i])
    return taskSH

def print_samples(sh):
    """Compactly print out contents of a SampleHandler"""
    logger.info('Number of samples: %i', len(sh))
    for s in sh:
        logger.info('Sample: %s', s.name())
        numFiles = s.numFiles()
        logger.info('  Number of files:  %i', numFiles)
        logger.info('  Number of events: %i', s.getNumEntries())
        for i in range(numFiles):
            logger.info('  %s', s.fileName(i))
