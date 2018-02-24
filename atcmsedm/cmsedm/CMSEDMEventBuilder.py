# Tai Sakuma <tai.sakuma@gmail.com>
from .CMSEDMEvents import CMSEDMEvents

from .cmsfilepath import convert_lfn_to_pfn_or_aaa

##__________________________________________________________________||
class CMSEDMEventBuilder(object):
    def __init__(self, config):
        self.config = config

    def __repr__(self):
        return '{}({!r})'.format(
            self.__class__.__name__,
            self.config
        )

    def __call__(self):
        paths = self.config.inputPaths
        paths = [convert_lfn_to_pfn_or_aaa(p) for p in self.config.inputPaths]
        events = CMSEDMEvents(
            paths = paths,
            maxEvents = self.config.maxEvents,
            start = self.config.start
        )
        events.config = self.config
        events.dataset = self.config.dataset.name
        return events

##__________________________________________________________________||
