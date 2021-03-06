# Tai Sakuma <tai.sakuma@cern.ch>
import os
import sys
import logging

import gzip

try:
   import cPickle as pickle
except:
   import pickle

import alphatwirl
from alphatwirl.misc.deprecation import _deprecated_class_method_option

from .yes_no import query_yes_no
from . import cmsedm

##__________________________________________________________________||
import logging
logger = logging.getLogger(__name__)
log_handler = logging.StreamHandler(stream=sys.stdout)
log_formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

##__________________________________________________________________||
class AtCMSEDM(object):
    """A simple framework for looping over Heppy flat trees with alphatwirl

    Args:
        quiet (bool): don't show progress bars if True
        parallel_mode (str): 'multiprocessing', 'subprocess', 'htcondor'
        dispatcher_options (dict): options to dispatcher
        process (int): the number of processes for the 'multiprocessing' mode
        user_modules (list of str): names of python modules to be copied for the 'subprocess' mode
        max_events_per_dataset (int): maximum number of events per data set
        max_events_per_process (int): maximum number of events per process (job)
        max_files_per_dataset (int): maximum number of files per data set
        max_files_per_process (int): maximum number of files per process (job)
        profile (bool): run cProfile if True
        profile_out_path (bool): path to store the result of the profile. stdout if None

    """
    @_deprecated_class_method_option('htcondor_job_desc_extra', msg='use dispatcher_options instead')
    def __init__(self,
                 quiet=False,
                 parallel_mode='multiprocessing',
                 htcondor_job_desc_extra=[ ],
                 dispatcher_options=dict(),
                 process=4,
                 user_modules=set(),
                 max_events_per_dataset=-1,
                 max_events_per_process=-1,
                 max_files_per_dataset=-1,
                 max_files_per_process=1,
                 profile=False,
                 profile_out_path=None
    ):
        user_modules = set(user_modules)
        user_modules.add('atcmsedm')
        self.parallel = alphatwirl.parallel.build_parallel(
           parallel_mode=parallel_mode,
           quiet=quiet,
           processes=process,
           user_modules=user_modules,
           ## htcondor_job_desc_extra=htcondor_job_desc_extra,
           dispatcher_options=dispatcher_options
        )
        self.max_events_per_dataset = max_events_per_dataset
        self.max_events_per_process = max_events_per_process
        self.max_files_per_dataset = max_files_per_dataset
        self.max_files_per_process = max_files_per_process
        self.profile = profile
        self.profile_out_path = profile_out_path
        self.parallel_mode = parallel_mode

    def run(self, datasets, reader_collector_pairs):
        self.parallel.begin()
        try:
            loop = self._configure(datasets, reader_collector_pairs)
            self._run(loop)
        except KeyboardInterrupt:
            logger = logging.getLogger(__name__)
            logger.warning('received KeyboardInterrupt')
            if query_yes_no('terminate running jobs'):
               logger.warning('terminating running jobs')
               self.parallel.terminate()
            else:
               logger.warning('not terminating running jobs')
        self.parallel.end()

    def _configure(self, datasets, reader_collector_pairs):
        reader_top = alphatwirl.loop.ReaderComposite()
        collector_top = alphatwirl.loop.CollectorComposite()
        for r, c in reader_collector_pairs:
            reader_top.add(r)
            collector_top.add(c)
        eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(self.parallel.communicationChannel)
        eventBuilderConfigMaker = cmsedm.EventBuilderConfigMaker()
        datasetIntoEventBuildersSplitter = alphatwirl.loop.DatasetIntoEventBuildersSplitter(
            EventBuilder=cmsedm.CMSEDMEventBuilder,
            eventBuilderConfigMaker=eventBuilderConfigMaker,
            maxEvents=self.max_events_per_dataset,
            maxEventsPerRun=self.max_events_per_process,
            maxFiles=self.max_files_per_dataset,
            maxFilesPerRun=self.max_files_per_process
        )
        eventReader = alphatwirl.loop.EventDatasetReader(
            eventLoopRunner=eventLoopRunner,
            reader=reader_top,
            collector=collector_top,
            split_into_build_events=datasetIntoEventBuildersSplitter
        )

        if self.parallel_mode in ('subprocess', 'htcondor'):
            loop = alphatwirl.datasetloop.ResumableDatasetLoop(
               datasets=datasets, reader=eventReader,
               workingarea=self.parallel.workingarea
            )
        else:
            loop = alphatwirl.datasetloop.DatasetLoop(datasets=datasets, reader=eventReader)

        return loop

    def _run(self, loop):
        if not self.profile:
            loop()
        else:
            alphatwirl.misc.print_profile_func(
               func=loop,
               profile_out_path=self.profile_out_path
            )

##__________________________________________________________________||
