import pyo
import numpy as np
from numpy.random import choice
import random
import wx
import process as pro
s = pyo.Server().boot()


class Audio:
    def __init__(self, mode=pro.LiveIn()):
        self.algo = pro.AsAmp()
        self.table = self.algo.table
        self.snd = self.algo.snd

    def refresh(self):
        self.algo = self.algo
        self.algo.refresh()
        self.table = self.algo.table
        self.snd = self.algo.snd
        

class Synth:
    def __init__(self):
        self.noi = pyo.Noise()
        self.filter = pyo.Biquad(self.noi)
        self.synth = pyo.Waveguide(self.filter, 200, .7)
        self.verb = pyo.WGVerb(self.synth).mix(2)

    
    def refresh(self):
        self.filter.freq = self.filter 
        self.synth.freq = self.param2 

    def setAmp(self, amp):
        self.noi.mul = amp*.01

    def setPitch(self, pitch):
        self.synth.freq = pitch*10

    def setFilter(self, freq):
        self.filter.freq = freq*100

    def setExtra(self, extra):
        self.synth.dur = extra*.1

    def defAmp(self):
        self.noi.mul = 1

    def defPitch(self):
        self.synth.freq = 440

    def defFilter(self):
        self.filter.freq = 1000

    def defExtra(self):
        self.synth.dur = .7

    def out(self):
        return self.verb.out()


class AsFrame(wx.Frame):
    def __init__(self, parent, title, pos, size, audio):
        wx.Frame.__init__(self, parent, id=-1, title=title, pos=pos, size=size)
        self.parent = parent
        self.audio = audio
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#444447")
        s.start()
        
        self.osc = Synth()
        self.osc.out()

        self.amps = ['as is', 'average', 'deviation', 'histogram', 'sections', 'markov']
        self.popup = wx.Choice(self.panel, id=-1, pos=(5,5), choices=self.amps)
        self.popup.SetSelection(0)
        self.popup.Bind(wx.EVT_CHOICE, self.changeAlgo)

        self.modes = ['file', 'live']
        self.popup2 = wx.Choice(self.panel, id=-1, pos=(95,5), choices=self.modes)
        self.popup2.SetSelection(0)
        self.popup2.Bind(wx.EVT_CHOICE, self.changeMode)    

        self.res = pyo.PyoGuiControlSlider(self.panel, 1, 100, init=50, pos=(130,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.resText = wx.StaticText(self.panel, id=-1, label="res", pos=(130,440))
        self.res.Bind(wx.EVT_LEFT_UP, self.setRes) 

        self.floorA = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=.01, pos=(190,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.floorAText = wx.StaticText(self.panel, id=-1, label="floorA", pos=(180,440))
        self.floorA.Bind(wx.EVT_LEFT_UP, self.changeFloorA) 

        self.ampA = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=100, pos=(250,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ampTextA = wx.StaticText(self.panel, id=-1, label="ampA", pos=(240,440))
        self.ampA.Bind(wx.EVT_LEFT_UP, self.changeAmp)

        self.lagA = pyo.PyoGuiControlSlider(self.panel, 0, 100, init=0, pos=(310,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.lagTextA = wx.StaticText(self.panel, id=-1, label="lagA", pos=(300,440))
        self.lagA.Bind(wx.EVT_LEFT_UP, self.setSmooth) 

        self.floorB = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=.01, pos=(370,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.floorBText = wx.StaticText(self.panel, id=-1, label="floorB", pos=(360,440))
        self.floorB.Bind(wx.EVT_LEFT_UP, self.changeFloorB) 

        self.ampB = pyo.PyoGuiControlSlider(self.panel, .01, 100, init=100, pos=(430,140), size=(25,300), log=True, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ampTextB = wx.StaticText(self.panel, id=-1, label="ampB", pos=(420,440))
        self.ampB.Bind(wx.EVT_LEFT_UP, self.changeAmpB)

        self.lagB = pyo.PyoGuiControlSlider(self.panel, 0, 100, init=0, pos=(490,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.lagTextB = wx.StaticText(self.panel, id=-1, label="lagB", pos=(480,440))
        self.lagB.Bind(wx.EVT_LEFT_UP, self.setSmoothB) 

        self.chooseButton = wx.Button(self.panel, id=-1, label="load sound", pos=(625,110))
        self.chooseButton.Bind(wx.EVT_BUTTON, self.loadSnd)   

        '''
        self.ctrl = pyo.PyoGuiControlSlider(self.panel, 1, 100, init=50, pos=(10,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.ctrlText = wx.StaticText(self.panel, id=-1, label="", pos=(0,440))
        '''
        self.ctrl = wx.Slider(self.panel, id=-1, value=50, minValue=1, maxValue=100, pos=(10,150), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.ctrlText = wx.StaticText(self.panel, id=-1, label="", pos=(0,440))
        
        self.checkOG = wx.CheckBox(self.panel, id=-1, label="reference sound", pos=(160,5), size=(-1, 20), style=0)
        self.checkOG.SetValue(True)
        self.checkOG.Bind(wx.EVT_CHECKBOX, self.OGsoundON) 

        self.SndVSizer = wx.BoxSizer(wx.VERTICAL)
        self.sndview = pyo.PyoGuiSndView(parent=self.panel, pos=(370,30), size=(300,200), style=0, )
        self.sndview.setTable(self.audio.algo.tableOG)
        self.sndview.setSelection(0, 1)
        self.sndview.Bind(pyo.EVT_PYO_GUI_SNDVIEW_SELECTION, self.setStSp)
        self.SndVSizer.Add(self.sndview, 1, wx.VERTICAL | wx.EXPAND, 5)


        self.checkTextA = wx.StaticText(self.panel, id=-1, label="A", pos=(570,220))
        self.checkTextB = wx.StaticText(self.panel, id=-1, label="B", pos=(570,270))        

        self.checkText1 = wx.StaticText(self.panel, id=-1, label="amp", pos=(600,180))
        self.checkText2 = wx.StaticText(self.panel, id=-1, label="pitch", pos=(670,180))
        self.checkText3 = wx.StaticText(self.panel, id=-1, label="filter", pos=(750,180))
        self.checkText4 = wx.StaticText(self.panel, id=-1, label="extra", pos=(810,180))


        self.checkAmpA = wx.CheckBox(self.panel, id=-1, label="", pos=(610,220), size=(-1, 20), style=0)
        self.checkAmpA.Bind(wx.EVT_CHECKBOX, self.setAmpA) 
    
        self.checkPitchA = wx.CheckBox(self.panel, id=-1, label="", pos=(680,220), size=(-1, 20), style=0)
        self.checkPitchA.Bind(wx.EVT_CHECKBOX, self.setPitchA) 

        self.checkFilterA = wx.CheckBox(self.panel, id=-1, label="", pos=(750,220), size=(-1, 20), style=0)
        self.checkFilterA.Bind(wx.EVT_CHECKBOX, self.setFilterA) 

        self.checkExtraA = wx.CheckBox(self.panel, id=-1, label="", pos=(820,220), size=(-1, 20), style=0)
        self.checkExtraA.Bind(wx.EVT_CHECKBOX, self.setExtraA) 


        self.checkAmpB = wx.CheckBox(self.panel, id=-1, label="", pos=(610,270), size=(-1, 20), style=0)
        self.checkAmpB.Bind(wx.EVT_CHECKBOX, self.setAmpB) 
    
        self.checkPitchB = wx.CheckBox(self.panel, id=-1, label="", pos=(680,270), size=(-1, 20), style=0)
        self.checkPitchB.Bind(wx.EVT_CHECKBOX, self.setPitchB) 

        self.checkFilterB = wx.CheckBox(self.panel, id=-1, label="", pos=(750,270), size=(-1, 20), style=0)
        self.checkFilterB.Bind(wx.EVT_CHECKBOX, self.setFilterB) 

        self.checkExtraB = wx.CheckBox(self.panel, id=-1, label="", pos=(820,270), size=(-1, 20), style=0)
        self.checkExtraB.Bind(wx.EVT_CHECKBOX, self.setExtraB) 
        
        vmainsizer = wx.BoxSizer()

        sizer7 = self.SndVSizer

        vmainsizer.Add(sizer7, 1, wx.BOTTOM | wx.LEFT, 350)
        self.panel.SetSizerAndFit(vmainsizer)
 
        self.Change()
        self.audio.algo.out()
    def Change(self):
        self.param1 = self.audio.algo.amp()
        self.param2 = self.audio.algo.amp2()

    '''
    def changeAlgo(self, evt):
        self.ctrl.Unbind(wx.EVT_LEFT_UP)            

            
        if self.popup.Selection == 0 :
            self.audio.algo = pro.AsAmp()
            
        elif self.popup.Selection == 1 :
            self.audio.algo = pro.AvgAmp()
            self.ctrl.SetValue(10)
            self.ctrl.SetRange(1,60)
            self.ctrlText.SetLabel("period")
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changePeriod)

        elif self.popup.Selection == 2 :
            self.audio.algo = pro.DevAmp()

        elif self.popup.Selection == 3 :
            self.audio.algo = pro.HistAmp()
            self.ctrl.SetValue(50)
            self.ctrl.SetRange(1,100)
            self.ctrlText.SetLabel('density')
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeDens) 

        elif self.popup.Selection == 4 :
            self.audio.algo = pro.SectAmp()
            self.ctrl.SetValue(3)
            self.ctrl.SetRange(1,100)
            self.ctrlText.SetLabel('length')
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeLength) 

        elif self.popup.Selection == 5 :
            self.audio.algo = pro.MarkAmp()
            self.ctrl.SetValue(1)
            self.ctrl.SetRange(1,5)
            self.ctrlText.SetLabel("order")
            self.ctrl.Bind(wx.EVT_LEFT_UP, self.changeOrder)   

        self.Change()    
        self.Refresh()
    '''

    def changeAlgo(self, evt):
        #self.ctrl.Unbind(wx.EVT_SCROLL_THUMBRELEASE)            

        if self.popup.Selection == 0 :
            self.audio.algo = pro.AsAmp()
            
        elif self.popup.Selection == 1 :
            self.audio.algo = pro.AvgAmp()
            self.ctrl.SetValue(10)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(60)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel("period 10")
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changePeriod)

        elif self.popup.Selection == 2 :
            self.audio.algo = pro.DevAmp()

        elif self.popup.Selection == 3 :
            self.audio.algo = pro.HistAmp()
            self.ctrl.SetValue(50)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(100)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel('density 50')
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeDens) 

        elif self.popup.Selection == 4 :
            self.audio.algo = pro.SectAmp()
            self.ctrl.SetValue(3)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(100)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel('length .03')
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeLength) 

        elif self.popup.Selection == 5 :
            self.audio.algo = pro.MarkAmp()
            self.ctrl.SetValue(1)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(5)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel("order 1")
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeOrder)   

        #self.Change()    
        self.Refresh()
    

    def changeMode(self, evt):
        if self.popup2.Selection == 0 :
            self.audio.algo.setMode(pro.SndReader())
        elif self.popup2.Selection == 1 :
            self.audio.algo.setMode(pro.LiveIn())
        self.audio.refresh()
        self.Change()    
        self.Refresh()
        


    def OGsoundON(self, evt):
        x = evt.IsChecked() 
        if x:
            self.audio.algo.out()
        else:
            self.audio.algo.stop()



    ''' 
    def changePeriod(self, evt):
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue()) 
        self.audio.algo.setPeriod(x)
        evt.Skip()

    def changeDens(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setDensity(x)
        evt.Skip()

    def changeLength(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setLength(x)
        evt.Skip()

    def changeOrder(self, evt):  
        if evt.LeftUp(): 
            x = int(self.ctrl.getValue())
        self.audio.algo.setOrder(x)
        evt.Skip()
    '''

    def changePeriod(self, evt):
        x = evt.GetInt()
        self.audio.algo.setPeriod(x)
        self.ctrlText.SetLabel("period %d" % x) 
        self.Change()   
    def changeDens(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setDensity(x)
        self.ctrlText.SetLabel("density %d" % x)
        self.Change()   
    def changeLength(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setLength(x)
        self.ctrlText.SetLabel("length %d" % x)
        self.Change()   
    def changeOrder(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setOrder(x)
        self.ctrlText.SetLabel("order %d" % x)
        self.Change()   
    

    def setRes(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setRes(x)
        self.Change()
        #self.resText.SetLabel("res")
        evt.Skip()

    def changeFloorA(self, evt):  
        if evt.LeftUp(): 
            x = self.floorA.getValue()* 100
        self.param1 += x
        #self.floorAText.SetLabel("floorA")
        evt.Skip()

    def changeAmp(self, evt): 
        if evt.LeftUp(): 
            x = self.ampA.getValue() * 1
        self.audio.algo.sig.mul = x
        #self.ampTextA.SetLabel("ampA")
        evt.Skip()

    def setSmooth(self, evt): 
        if evt.LeftUp(): 
            x = self.lagA.getValue() * .01
        self.audio.algo.sig.time = x
        #self.lagTextA.SetLabel("lagA")
        evt.Skip()


    def changeFloorB(self, evt):  
        if evt.LeftUp(): 
            x = self.floorB.getValue()* 100
        self.param2 += x
        #self.floorBText.SetLabel("floorB")
        evt.Skip()

    def changeAmpB(self, evt):
        if evt.LeftUp(): 
            x = self.ampB.getValue() * 1
        self.audio.algo.sig2.mul = x
        #self.ampTextB.SetLabel("ampB")
        evt.Skip()

    def setSmoothB(self, evt):  
        if evt.LeftUp(): 
            x = self.lagB.getValue() * .01
        self.audio.algo.sig2.time = x
        #self.lagTextB.SetLabel("lagB")
        evt.Skip()


    def loadSnd(self, evt):
        wildcard = "All files|*.*|" \
               "AIFF file|*.aif;*.aiff;*.aifc;*.AIF;*.AIFF;*.Aif;*.Aiff|" \
               "Wave file|*.wav;*.wave;*.WAV;*.WAVE;*.Wav;*.Wave"
        self.dlg = wx.FileDialog(self, message="Choose a new soundfile...", wildcard=wildcard, style=wx.FD_OPEN)
        if self.dlg.ShowModal() == wx.ID_OK:
            path = self.dlg.GetPath()
            if path != "":
                self.audio.algo.setSound(path)

        self.dlg.Destroy()
        self.sndview.setTable(self.audio.algo.tableOG)
        self.Change()
        self.Refresh()    


    def setStSp(self, evt):
        self.audio.algo.setStartStop((evt.value[0]*self.audio.algo.durOG), (evt.value[1]*self.audio.algo.durOG))
        self.Change()
        self.Refresh() 


    def setAmpA(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setAmp(self.param1)
        else:
            self.osc.defAmp()  

    def setFilterA(self, evt):
        x = evt.IsChecked() 
        if x: 
            self.osc.setFilter(self.param1)  
        else:
            self.osc.defFilter() 

    def setPitchA(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setPitch(self.param1)  
        else:
            self.osc.defPitch() 

    def setExtraA(self, evt):
        x = evt.IsChecked() 
        if x:   
            self.osc.setExtra(self.param1)  
        else:
            self.osc.defExtra() 


    def setAmpB(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setAmp(self.param2)
        else:
            self.osc.defAmp()  

    def setFilterB(self, evt):
        x = evt.IsChecked() 
        if x: 
            self.osc.setFilter(self.param2)  
        else:
            self.osc.defFilter() 

    def setPitchB(self, evt):
        x = evt.IsChecked() 
        if x:
            self.osc.setPitch(self.param2)  
        else:
            self.osc.defPitch() 

    def setExtraB(self, evt):
        x = evt.IsChecked() 
        if x:   
            self.osc.setExtra(self.param2)  
        else:
            self.osc.defExtra() 



app = wx.App()

aud = Audio()
mainFrame = AsFrame(None, title='asaps', pos=(100,100), size=(1000,500), audio=aud)
mainFrame.Show()

app.MainLoop()



