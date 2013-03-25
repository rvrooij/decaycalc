#!/usr/bin/env python
import Tkinter as tk
from datetime import datetime, timedelta
from math import log

class LabelEntry(tk.Frame):
    def __init__(self, master, text, state=tk.NORMAL, size=0):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(1, minsize=size)
        self.v = tk.StringVar()
        tk.Label(self, text=text).grid(row=0, column=0)
        self.entry = tk.Entry(self, textvariable=self.v, state=state, width=14)
        self.entry.grid(row=0, column=1, sticky="EW")
    def set(self, value):
        return self.v.set(value)
    def get(self):
        return self.v.get()
    def color(self, color):
        self.entry.config(fg=color)    

class LabelOptionMenu(tk.Frame):
    def __init__(self, master, text, variable, optionlist, command=None, size=0):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(1, minsize=size)
        tk.Label(self, text=text).grid(row=0, column=0, sticky="W")
        tk.OptionMenu(self, variable, *optionlist, command=command).grid(row=0, column=1, sticky="EW")

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
        self.datetime_format = "%d-%m-%Y %H:%M"
        
        self.selected_preset = tk.StringVar()
        self.selected_isotope = tk.StringVar()
        self.show_halflife = tk.StringVar()
        
        isotope_list = [
            Isotope(18, "F", 109.771, "m"),
            Isotope(99, "mTc", 6.00718, "h", label="99m-Tc"),
            Isotope(68, "Ge", 270.95, "d"),
            Isotope(166, "Ho", 26.8, "h"),
            Isotope(123, "I", 13.22, "h"),
        ]
        self.isotopes = {}
        for i in isotope_list:
            self.isotopes[i.label] = i
        
        self.presets = {
            "FDG vandaag": {
                "selected_isotope": "18-F",
                "t0": datetime.now().strftime(self.datetime_format),
                "t1": '',
                "A0": 100.0,
                "A1": 50.0,
            },
            "Oude tonnetje": {
                "selected_isotope": "68-Ge",
                "t0": datetime(2010, 11, 10, 12, 00).strftime(self.datetime_format),
                "t1": datetime.now().strftime(self.datetime_format),
                "A0": 83.58,
                "A1": '',
            },
            "Nieuwe tonnetje": {
                "selected_isotope": "68-Ge",
                "t0": datetime(2012, 6, 1, 12, 00).strftime(self.datetime_format),
                "t1": datetime.now().strftime(self.datetime_format),
                "A0": 74.41,
                "A1": '',
            }
        }
        
        self.build_widgets()
        self.selected_preset.set("FDG vandaag")
        self.change_preset()
    
    def build_widgets(self):
        isotopelist = [i.label for i in self.isotopes.values()]
        isotopelist.sort(key=lambda i: self.isotopes[i].mass)
        
        self.resizable(0,0)
        size=150
        
        LabelOptionMenu(self, "Isotope:", self.selected_isotope, isotopelist, command=self.change_halflife, size=size).grid(row=0,column=0, sticky="E", padx=5)
        self.t0 = LabelEntry(self, "Time 0:", size=size)
        self.t0.grid(row=1, column=0, sticky="E", padx=5)
        self.t1 = LabelEntry(self, "Time 1:", size=size)
        self.t1.grid(row=2, column=0, sticky="E", padx=5)
        self.dt = LabelEntry(self, "Delta:", state="readonly", size=size)
        self.dt.grid(row=3, column=0, sticky="E", padx=5)
        LabelOptionMenu(self, "Preset:", self.selected_preset, self.presets.keys(), command=self.change_preset, size=size).grid(row=4, column=0, sticky="E", padx=5)
        
        tk.Label(self, textvariable=self.show_halflife).grid(row=0, column=1, padx=5)
        self.A0 = LabelEntry(self, "Activity 0:", size=size)
        self.A0.grid(row=1, column=1, sticky="E", padx=5)
        self.A1 = LabelEntry(self, "Activity 1:", size=size)
        self.A1.grid(row=2, column=1, sticky="E", padx=5)
        self.dA = LabelEntry(self, "Ratio:", state="readonly", size=size)
        self.dA.grid(row=3, column=1, sticky="E", padx=5)
        tk.Button(self, text="Calculate", command=self.calculate).grid(row=4, column=1, padx=5)
        
        self.message = tk.Label(self, text='', fg='red', relief="sunken")
        self.message.grid(row=5, column=0, columnspan=2, sticky="EW")
    
    def change_halflife(self, e=None):
        x = self.isotopes[self.selected_isotope.get()]
        text = "Halflife: %s %s"%(x.halflife, x.units)
        self.show_halflife.set(text)
    
    def change_preset(self, e=None):
        preset = self.presets[self.selected_preset.get()]
        for key, value in preset.items():
            getattr(self, key).set(value)
            
        self.message.config(text='')
        self.change_halflife()    
        self.calculate()

    def gather_variables(self):
        encountered_error = False
        val = {}
        for key, time in {"t0": self.t0, "t1": self.t1}.items():
            if time.get():
                try:
                    val[key] = datetime.strptime(time.get(), self.datetime_format)
                    time.color('black')
                except ValueError:
                    val[key] = None
                    encountered_error = True
                    time.color('red')       
        
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
        
        halflife = self.isotopes[self.selected_isotope.get()].halflife_in_seconds
        calc = [item for item in ("t0", "t1", "A0", "A1") if item not in val][0]
        if calc == "A1":
            dt = (val["t1"]-val["t0"])
            s = val["A0"] * 0.5**(dt.total_seconds()/halflife)
            self.A1.set(s)
        elif calc == "A0":
            dt = (val["t0"]-val["t1"])
            s = val["A1"] * 0.5**(dt.total_seconds()/halflife)
            self.A0.set(s)
        else:
            sec = halflife * log(val["A0"]/val["A1"], 2)
            dt = timedelta(seconds=sec)
            if calc == "t0":
                self.t0.set( (val["t1"] - dt).strftime(self.datetime_format) )
            else:
                self.t1.set( (val["t0"] + dt).strftime(self.datetime_format) )
        
        self.dA.set("%.3f"%(float(self.A1.get())/float(self.A0.get())))
        self.dt.set(dt)

if __name__ == "__main__":
    app = DecayApp(None)
    app.mainloop()
