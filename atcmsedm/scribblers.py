# Tai Sakuma <sakuma@cern.ch>


from DataFormats.FWLite import Handle
# https://github.com/cms-sw/cmssw/blob/CMSSW_8_1_X/DataFormats/FWLite/python/__init__.py

##__________________________________________________________________||
class EventAuxiliary(object):
    # https://github.com/cms-sw/cmssw/blob/CMSSW_8_1_X/DataFormats/Provenance/interface/EventAuxiliary.h

    def begin(self, event):
        self.run = [ ]
        self.lumi = [ ]
        self.eventId = [ ]
        self._attach_to_event(event)

    def _attach_to_event(self, event):
        event.run = self.run
        event.lumi = self.lumi
        event.eventId = self.eventId

    def event(self, event):
        self._attach_to_event(event)

        eventAuxiliary = event.edm_event.eventAuxiliary()
        self.run[:] = [eventAuxiliary.run()]
        self.lumi[:] = [eventAuxiliary.luminosityBlock()]
        self.eventId[:] = [eventAuxiliary.event()]

##__________________________________________________________________||
class MET(object):
    """ a simple example scribbler

    """
    def begin(self, event):
        self.met = [ ]
        self._attach_to_event(event)

        self.handle = Handle("std::vector<pat::MET>")

    def _attach_to_event(self, event):
        event.met = self.met

    def event(self, event):
        self._attach_to_event(event)

        edm_event = event.edm_event

        edm_event.getByLabel("slimmedMETs", self.handle)
        met = self.handle.product().front()
        self.met[:] = [met.pt()]

    def end(self):
        self.handle = None

##__________________________________________________________________||
