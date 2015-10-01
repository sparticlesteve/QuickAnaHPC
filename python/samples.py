import os
from setup import logger

def scan_samples(scanDir, samplePatterns = []):
    """Scan a filesystem and build a SampleHandler"""
    from ROOT import SH
    sh = SH.SampleHandler()
    sh.setMetaString('nc_tree', 'CollectionTree')
    scanDir = os.path.expandvars(args.scanDir)
    patterns = ['*'+p+'*' for p in args.samplePattern]
    if len(patterns) == 0: patterns = ['*']
    for pattern in patterns:
        SH.ScanDir().samplePattern(pattern).scan(sh, scanDir)
    return sh

def split_samples(sh, num_events=1000):
    """
    Split a sample handler's samples into smaller samples of size num_events.
    This function does not split individual files.
    """
    from ROOT import SH
    splitSH = SH.SampleHandler()
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
    for i in xrange(task_id, len(sh), num_tasks):
        taskSH.add(sh[i])
    return taskSH

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
        sh = scan_samples(args.scanDir, args.samplePatterns)
    # Choose samples according to task ID
    if args.task:
        task, numTasks = map(int, args.task.split(':'))
        sh = select_by_task(sh, task, numTasks)
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
