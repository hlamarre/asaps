import pyo
import numpy as np
from numpy.random import choice
import random
import wx
import process as pro
s = pyo.Server().boot()


class Audio:
    def __init__(self):
        self.algo = pro.AsAmp()
        self.table = self.algo.table
        self.snd = pro.SndReader()
        #self.algo.setStartStop(start=20,stop=40)

        #self.algo.snd = self.snd
        #self.algo.out()
        self.pitch = pro.HpsPit(self.algo.amp())


'''
class Synth:
    def __init__(self, freq=0, mul=0):
        self.freq = freq
        self.mul = mul
        self.osc = pyo.Sine(self.freq, self.mul).out()

    def out(self):
        return self.osc
'''




class AsFrame(wx.Frame):
    def __init__(self, parent, title, pos, size, audio):
        wx.Frame.__init__(self, parent, id=-1, title=title, pos=pos, size=size)
        self.parent = parent
        self.audio = Audio()
        self.audio.algo.setStartStop(20,40)
        #self.pitch = self.audio.freqs() 
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("#555555")
        s.start()


        self.osc = pyo.Sine(400, 0).out()


        self.amps = ['as is', 'average', 'deviation', 'histogram', 'sections', 'markov']
        self.popup = wx.Choice(self.panel, id=-1, pos=(5,5), choices=self.amps)
        self.popup.SetSelection(0)
        self.popup.Bind(wx.EVT_CHOICE, self.changeAlgo)

        self.modes = ['file', 'live']
        self.popup2 = wx.Choice(self.panel, id=-1, pos=(95,5), choices=self.modes)
        self.popup2.SetSelection(0)
        self.popup2.Bind(wx.EVT_CHOICE, self.changeMode)    

        #self.res = wx.Slider(self.panel, id=-1, value=50, minValue=1, maxValue=100, pos=(130,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.res = pyo.PyoGuiControlSlider(self.panel, 1, 100, init=50, pos=(130,140), size=(25,300), log=False, integer=False, powoftwo=False, orient=wx.VERTICAL)
        self.resText = wx.StaticText(self.panel, id=-1, label="res", pos=(130,440))
        self.res.Bind(wx.EVT_LEFT_UP, self.setRes) 

        self.vol = wx.Slider(self.panel, id=-1, value=0, minValue=0, maxValue=100, pos=(190,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.volText = wx.StaticText(self.panel, id=-1, label="vol 0", pos=(180,440))
        self.vol.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeVol) 

        self.ampA = wx.Slider(self.panel, id=-1, value=100, minValue=0, maxValue=100, pos=(250,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.ampTextA = wx.StaticText(self.panel, id=-1, label="amp-A 1", pos=(240,440))
        self.ampA.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeAmp)#wx.EVT_LEFT_UP  EVT.skip dans la m/thode

        self.lagA = wx.Slider(self.panel, id=-1, value=0, minValue=0, maxValue=100, pos=(310,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.lagTextA = wx.StaticText(self.panel, id=-1, label="lag-A .01", pos=(300,440))
        self.lagA.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.setSmooth) 

        self.ampB = wx.Slider(self.panel, id=-1, value=100, minValue=0, maxValue=100, pos=(370,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.ampTextB = wx.StaticText(self.panel, id=-1, label="amp-B 1", pos=(360,440))
        self.ampB.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeAmpB)

        self.lagB = wx.Slider(self.panel, id=-1, value=0, minValue=0, maxValue=100, pos=(430,140), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.lagTextB = wx.StaticText(self.panel, id=-1, label="lag-B .01", pos=(410,440))
        self.lagB.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.setSmoothB) 

        self.chooseButton = wx.Button(self.panel, id=-1, label="load sound", pos=(625,110))
        self.chooseButton.Bind(wx.EVT_BUTTON, self.loadSnd)   

        self.ctrl = wx.Slider(self.panel, id=-1, value=50, minValue=1, maxValue=100, pos=(10,150), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
        self.ctrlText = wx.StaticText(self.panel, id=-1, label="", pos=(0,440))
       
        self.SndVSizer = wx.BoxSizer(wx.VERTICAL)
        self.sndview = pyo.PyoGuiSndView(parent=self.panel, pos=(370,30), size=(300,200), style=0, )
        self.sndview.setTable(self.audio.algo.tableOG)
        self.sndview.setSelection(0, 1)
        self.sndview.Bind(pyo.EVT_PYO_GUI_SNDVIEW_SELECTION, self.setStSp)
        self.SndVSizer.Add(self.sndview, 1, wx.VERTICAL | wx.EXPAND, 5)
        
        vmainsizer = wx.BoxSizer()

        sizer7 = self.SndVSizer

        vmainsizer.Add(sizer7, 1, wx.BOTTOM | wx.LEFT, 350)
        self.panel.SetSizerAndFit(vmainsizer)
 
    def Change(self):
        self.osc.mul = self.audio.algo.amp()
        self.osc.freq = self.audio.pitch.getPitch()




    def changeAlgo(self, evt):
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
            self.ctrlText.SetLabel('thresh .03')
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeThresh) 

            self.length = wx.Slider(self.panel, id=-1, value=4, minValue=1, maxValue=100, pos=(70,150), size=(-1,300), style=wx.SL_VERTICAL | wx.SL_INVERSE)
            self.lengthText = wx.StaticText(self.panel, id=-1, label="length    ", pos=(60,440))
            self.length.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeLength) 

        elif self.popup.Selection == 5 :
            self.audio.algo = pro.MarkAmp()
            self.ctrl.SetValue(1)
            self.ctrl.SetMin(1)
            self.ctrl.SetMax(5)
            self.ctrl.style = wx.SL_VERTICAL | wx.SL_INVERSE
            self.ctrlText.SetLabel("order 1")
            self.ctrl.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.changeOrder)   

        self.Change()    
        self.Refresh()

    def changeMode(self, evt):
        if self.popup.Selection == 0 :
            self.audio.algo.setMode(pro.SndReader())
        elif self.popup.Selection == 1 :
            self.audio.algo.setMode(pro.LiveIn())
        self.Change()    
        self.Refresh()

    def changePeriod(self, evt):
        x = evt.GetInt()
        self.audio.algo.setPeriod(x)
        self.ctrlText.SetLabel("period %d" % x)    
    def changeDens(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setDensity(x)
        self.ctrlText.SetLabel("density %d" % x)
    def changeThresh(self, evt):  
        x = evt.GetInt() * .01
        self.audio.algo.setThresh(x)
        self.ctrlText.SetLabel("thresh %.2f" % x)
    def changeLength(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setLength(x)
        self.lengthText.SetLabel("length %d" % x)
    def changeOrder(self, evt):  
        x = evt.GetInt()
        self.audio.algo.setOrder(x)
        self.ctrlText.SetLabel("order %d" % x)


    def setRes(self, evt):  
        if evt.LeftUp(): 
            x = self.res.getValue() 
        self.audio.algo.setRes(x)
        self.Change()
        self.resText.SetLabel("res")
        evt.Skip()

    def changeVol(self, evt):  
        x = evt.GetInt() * .01
        self.osc.mul += x
        self.volText.SetLabel("vol %.2f" % x)

    def changeAmp(self, evt):  
        x = evt.GetInt() * .01
        self.audio.algo.sig.mul = x
        self.ampTextA.SetLabel("amp-A %.2f" % x)

    def setSmooth(self, evt):  
        x = evt.GetInt() * .01
        self.audio.algo.sig.time = x
        self.lagTextA.SetLabel("lag-A %.2f" % x)

    def changeAmpB(self, evt):  
        x = evt.GetInt() * .01
        self.audio.algo.sig2.mul = x
        self.ampTextA.SetLabel("amp-A %.2f" % x)

    def setSmoothB(self, evt):  
        x = evt.GetInt() * .01
        self.audio.algo.sig2.time = x
        self.lagTextA.SetLabel("lag-A %.2f" % x)

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
        #self.Refresh() 


app = wx.App()

aud = Audio()
mainFrame = AsFrame(None, title='asaps', pos=(100,100), size=(1000,500), audio=aud)
mainFrame.Show()


app.MainLoop()





