#!/usr/bin/env python

import Tkinter as tk
import datetime
import time
import math

class LabelEntry(tk.Frame):
    def __init__(self, master, text, state=tk.NORMAL):
        self.v = tk.StringVar()
        tk.Frame.__init__(self, master)
        tk.Label(self, text=text).grid(row=0, column=0)
        self.entry = tk.Entry(self, textvariable=self.v, state=state, width=16)
        self.entry.grid(row=0, column=1)
    def set(self, value):
        return self.v.set(value)
    def get(self):
        return self.v.get()
    def color(self, color):
        self.entry.config(fg=color)    

class LabelOptionMenu(tk.Frame):
    def __init__(self, master, text, variable, optionlist, command=None):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text=text).grid(row=0, column=0, sticky="W")
        tk.OptionMenu(self, variable, *optionlist, command=command).grid(row=0, column=1, sticky="E")

class Isotope(object):
    def __init__(self, mass, name, halflife, units, label=None):
        self.mass = mass
        self.name = name
        self.units = units
        self.halflife = halflife
        seconds_in = {"m": 60,
                      "h": 60*60,
                      "d": 60*60*24}
        self.halflife_in_seconds = halflife * seconds_in[units]
        self.label = label
        if not self.label:
            self.label = "%s-%s"%(self.mass, self.name)
        

class DecayApp(tk.Tk):
    def __init__(self, master=None):
        tk.Tk.__init__(self, master)
        self.title("Stralingstool 1.0")
        
        self.default = tk.StringVar()
        self.isotope = tk.StringVar()
        self.show_halflife = tk.StringVar()
        
        isotopes = [
            Isotope(18, "F", 109.771, "m"),
            Isotope(99, "mTc", 6.00718, "h", label="99m-Tc"),
            Isotope(68, "Ge", 270.95, "d"),
            Isotope(166, "Ho", 26.8, "h"),
            Isotope(123, "I", 13.22, "h"),
        ]
        self.halflife = {}
        for i in isotopes:
            self.halflife[i.label] = i
        
        '''
        #Name of isotope must be of form int-str to sort the isotopelist
        self.halflife = {"18-F": [109.771,"m"],
                         "99-mTc": [6.00718,"h"],
                         "68-Ge": [270.95,"d"],
                         "166-Ho": [26.8, "h"],
                         "123-I": [13.22, "h"]}
                         
        seconds_in = {"m": 60,
                      "h": 60*60,
                      "d": 60*60*24}
                      
        for data in self.halflife.values():
            #Adds the halflife in seconds for each isotope in self.halflife
            sec = data[0]*seconds_in[data[1]]
            data = data.append(sec)
        '''
        self.build_widgets()
    
    def build_widgets(self):
        defaultlist = ["FDG vandaag", "Oude tonnetje", "Nieuwe tonnetje"]
        #isotopelist = self.halflife.keys()
        #isotopelist.sort(key=lambda x:int(x.split('-')[0]) )
        isotopelist = [self.halflife[key].label for key in sorted(self.halflife.keys(), key=lambda x:self.halflife[x].mass )]
        
        LabelOptionMenu(self, "Preset:", self.default, defaultlist, command=self.changeDefault).grid(row=0, column=0, sticky="EW")
        
        self.d0 = LabelEntry(self, "Date 0:")
        self.d0.grid(row=1, column=0, sticky="E")
        self.d1 = LabelEntry(self, "Date 1:")
        self.d1.grid(row=2, column=0, sticky="E")
        self.message = tk.Label(self, text='', fg='red')
        self.message.grid(row=3, column=0)
        tk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=0)
        
        self.t0 = LabelEntry(self, "Time 0:")
        self.t0.grid(row=1, column=1, sticky="E", padx=10)
        self.t1 = LabelEntry(self, "Time 1:")
        self.t1.grid(row=2, column=1, sticky="E", padx=10)
        self.dt = LabelEntry(self, "Delta:", state="readonly")
        self.dt.grid(row=3, column=1, sticky="E", padx=10)
        LabelOptionMenu(self, "Isotope:", self.isotope, isotopelist, command=self.changeHalflife).grid(row=4,column=1, sticky="EW", padx=10)
        
        self.A0 = LabelEntry(self, "Activity 0:")
        self.A0.grid(row=1, column=2, sticky="E")
        self.A1 = LabelEntry(self, "Activity 1:")
        self.A1.grid(row=2, column=2, sticky="E")
        self.dA = LabelEntry(self, "Ratio:", state="readonly")
        self.dA.grid(row=3, column=2, sticky="E")
        tk.Label(self, textvariable=self.show_halflife).grid(row=4, column=2, sticky="W")
        
        self.default.set(defaultlist[0])
        self.changeDefault()
        self.changeHalflife()
    
    def changeHalflife(self, e=None):
        x = self.halflife[self.isotope.get()]
        #text = "Halflife: " + str(x[0]) + " " + x[1]
        text = "Halflife: %s %s"%(x.halflife, x.units)
        self.show_halflife.set(text)
    
    def changeDefault(self, e=None):
        now = datetime.datetime.now()
        self.d1.set(now.strftime("%d-%m-%Y"))
        self.t1.set(now.strftime("%H:%M"))
        self.A1.set('')
        if self.default.get() == "FDG vandaag":
            self.d0.set(self.d1.get())
            self.t0.set(self.t1.get())
            self.A0.set(100.0)
            self.isotope.set("18-F")
        elif self.default.get() == "Oude tonnetje":
            self.d0.set("10-11-2010")
            self.t0.set("12:00")
            self.A0.set(83.58)
            self.isotope.set("68-Ge")
        elif self.default.get() == "Nieuwe tonnetje":
            self.d0.set("1-6-2012")
            self.t0.set("12:00")
            self.A0.set(74.41)
            self.isotope.set("68-Ge")
        
        self.changeHalflife()    
        self.calculate()
        self.message.config(text='')
    
    def getSecondsFromDate(self, d):
        dt = time.strptime(d.get(), "%d-%m-%Y")
        return time.mktime(dt)
    
    def getSecondsFromTime(self, t):
        dt = time.strptime(t.get(), "%H:%M")
        sec = datetime.timedelta(hours=dt.tm_hour,minutes=dt.tm_min).total_seconds()
        return sec

    def gather_variables(self):
        encountered_error = False
        val = {}
        for key, time in {"t0": self.t0, "t1": self.t1}.items():
            date = {"t0": self.d0, "t1": self.d1}[key]
            if date.get() and time.get():
                try:
                    sec = self.getSecondsFromDate(date)
                    date.color('black')
                except ValueError:
                    encountered_error = True
                    date.color('red')
                try:
                    sec += self.getSecondsFromTime(time)
                    time.color('black')
                except ValueError:
                    encountered_error = True
                    time.color('red')
                val[key] = sec             
        
        for key, value in {"A0": self.A0, "A1": self.A1}.items():
            if value.get():
                try:
                    val[key] = float(value.get())
                    value.color('black')
                except ValueError:
                    val[key] = None
                    encountered_error = True
                    value.color('red')
                
        if len(val) < 3:
            encountered_error = True
            self.message.config(text="Need more info")
        elif len(val) > 3:
            encountered_error = True
            self.message.config(text="Clear one value")
        else:
            self.message.config(text="")
        
        if encountered_error:
            val = {}
        
        return val
        
    def calculate(self):
        val = self.gather_variables()
        if not val: return
        calc = [item for item in ("t0", "t1", "A0", "A1") if item not in val][0]
        
        #halflife = self.halflife[self.isotope.get()][2]
        halflife = self.halflife[self.isotope.get()].halflife_in_seconds
        
        if calc == "A1":
            dt = val["t1"]-val["t0"]
            s = val["A0"] * 0.5**(dt/halflife)
            self.A1.set(s)
        elif calc == "A0":
            dt = val["t1"]-val["t0"]
            s = val["A1"] * 2**((val["t1"]-val["t0"])/halflife)
            self.A0.set(s)
        else:
            dt = halflife * math.log(val["A0"]/val["A1"],2)
            if calc is "t0":
                d_var = self.d0
                t_var = self.t0
                sec = val["t1"] - dt
            else:
                d_var = self.d1
                t_var = self.t1
                sec = val["t0"] + dt
                
            stamp = datetime.datetime.fromtimestamp(sec)
            d_var.set( stamp.strftime("%d-%m-%Y") )
            t_var.set( stamp.strftime("%H:%M") )
        
        self.dA.set("%.3f"%(float(self.A1.get())/float(self.A0.get())))
        delta = datetime.timedelta(seconds=dt)
        self.dt.set(delta)

if __name__ == "__main__":
    app = DecayApp()
    app.mainloop()
