# Tai Sakuma <tai.sakuma@gmail.com>
import os
import logging

try:
    from DataFormats.FWLite import Events as EDMEvents
    # https://github.com/cms-sw/cmssw/blob/CMSSW_9_1_X/DataFormats/FWLite/python/__init__.py
except ImportError:
    pass

from .EventBuilderConfig import EventBuilderConfig
from .load_fwlite import load_fwlite

from .cmsfilepath import convert_lfn_to_pfn_or_aaa

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self):
        pass

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            treeName = self.treeName,
            maxEvents = length,
            start = start,
            dataset = dataset, # for scribblers
            name = dataset.name # for the progress report writer
        )
        return config

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths = files,
            maxEvents = length,
            start = start,
            dataset = dataset, # for scribblers
            name = dataset.name # for the progress report writer
        )
        return config

    def file_list_in(self, dataset, maxFiles):
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(dataset.files))]

    def nevents_in_file(self, path):
        load_fwlite()
        path = convert_lfn_to_pfn_or_aaa(path)
        edm_event = EDMEvents([path])
        return edm_event.size()

##__________________________________________________________________||
