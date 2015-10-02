# QuickAnaHPC

This package contains some testing code for running a QuickAna-based analysis
application on HPCs such as Edison (and eventually Cori). For the sake of
comparisons, functionality is included to run the application in various modes
using a few different EventLoop drivers. The application can run directly on
an interactive node, can run on the PDSF batch system, and can run using
PROOF-lite on either a local node or a batch system like Edison.

## Overview

The application is based on EventLoop and QuickAna. It processes systematics
and applies the (mostly default) object definitions of QuickAna. The output
is currently a set of kinematic histograms for each systematic. Python is used
to configure, steer, and submit the application to various EventLoop backends.

## Contents of the package

* [AnalysisAlg](QuickAnaHPC/AnalysisAlg.h) - A simple EventLoop Algorithm for
  running QuickAna. It has a configuration flag for disabling systematics. It
  books and fills the output histograms.
* [runQuickAnaHPC.py](scripts/runQuickAnaHPC.py) - Executable python script
  which configures and launches the application. Has several command line
  options for specifying the input samples, the driver to use, and various
  other job configuration options.
  * The `--task ID:N` option allows to specify a chunk of the input data for
    processing. The process will only use the ID-th chunk of size 1/N of the
    input samples. If samples are broken up into individual files, this is a
    useful way to distribute files evenly across separately submitted tasks.
* [Python modules](python) - Utility code for sample management, logging, and
  loading RootCore libraries. Can be expanded as necessary. I may move some
  machine-specific or driver-specific setups in here.
* Edison example submission scripts in [scripts](scripts).
