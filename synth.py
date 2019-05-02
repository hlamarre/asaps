import pyo

class Synth:
    # parent

    def __init__(self):
        self.synth = pyo.Sine(200)
        self.filter = pyo.Biquad(self.synth)
        self.verb = pyo.WGVerb(self.synth).mix(2)

    
    def refresh(self):
        self.filter.freq = self.filter 
        self.synth.freq = self.param2 

    def setAmp(self, amp):
        self.synth.mul = amp*.01

    def setPitch(self, pitch):
        self.synth.freq = pitch*10

    def setFilter(self, freq):
        self.filter.freq = freq*100

    def setExtra(self, extra):
        self.synth.dur = extra*.1

    def defAmp(self):
        self.synth.mul = 1

    def defPitch(self):
        self.synth.freq = 440

    def defFilter(self):
        self.filter.freq = 1000

    def defExtra(self):
        self.verb.cutoff = .7

    def out(self):
        return self.verb.out()

    def stop(self):
        self.synth.stop()


class WvGd(Synth):
    # waveguide
    def __init__(self):
        super().__init__()
        self.noi = pyo.Noise()
        self.filter = pyo.Biquad(self.noi)
        self.synth = pyo.Waveguide(self.filter, 200, .7)
        self.verb = pyo.WGVerb(self.synth).mix(2)

    def setAmp(self, amp):
        self.noi.mul = amp*.01

    def setExtra(self, extra):
        self.synth.dur = extra*.1

    def defAmp(self):
        self.noi.mul = 1

    def defExtra(self):
        self.synth.dur = .7


class FM(Synth):
    # FM
    def __init__(self):
        super().__init__()
        self.synth = pyo.CrossFM()
        self.verb = pyo.WGVerb(self.synth).mix(2)

    def setAmp(self, amp):
        self.synth.mul = amp*.01

    def setPitch(self, pitch):
        self.synth.carrier = pitch*2

    def setFilter(self, freq):
        self.synth.ratio = freq

    def setExtra(self, extra):
        self.synth.ind1 = extra*.1

    def defAmp(self):
        self.synth.mul = 1

    def defPitch(self):
        self.synth.carrier = 440

    def defFilter(self):
        self.synth.ratio = 1

    def defExtra(self):
        self.synth.ind1 = 1

    def out(self):
        return self.verb.out()


class WT(Synth):
    # wavetable
    def __init__(self):
        super().__init__()
        
        self.sine = pyo.CosTable([(0,0), (100,1), (1000,.25), (8191,0)])
        self.square = pyo.SquareTable()
        self.saw = pyo.SawTable()
        self.synth = pyo.NewTable(8192/44100)

        self.pointer = pyo.Sig(0)
        self.morph = pyo.TableMorph(self.pointer, self.synth, [self.sine, self.square, self.saw])
        self.osc = pyo.Osc(self.synth, 440)
        self.filter = pyo.Biquad(self.osc)
        self.verb = pyo.WGVerb(self.filter).mix(2)

    def setAmp(self, amp):
        self.osc.mul = amp*.01

    def setPitch(self, pitch):
        self.osc.freq = pitch*10

    def setFilter(self, freq):
        self.filter.freq = freq*100

    def setExtra(self, extra):
        self.pointer.setValue(extra*.1)

    def defAmp(self):
        self.osc.mul = 1

    def defPitch(self):
        self.osc.freq = 440

    def defFilter(self):
        self.filter.freq = 1000

    def defExtra(self):
        self.pointer.value = 0

    def stop(self):
        self.osc.stop()



if __name__ == "__main__":
    s = pyo.Server().boot()

    syn = WT()
    syn.out()

    s.gui(locals())