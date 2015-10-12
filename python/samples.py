import os
from setup import logger

def scan_samples(scanDir, samplePatterns = []):
    """Scan a filesystem and build a SampleHandler"""
    from ROOT import SH
    sh = SH.SampleHandler()
    sh.setMetaString('nc_tree', 'CollectionTree')
    scanDir = os.path.expandvars(scanDir)
    patterns = ['*'+p+'*' for p in samplePatterns]
    if len(patterns) == 0: patterns = ['*']
    for pattern in patterns:
        SH.ScanDir().samplePattern(pattern).scan(sh, scanDir)
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
