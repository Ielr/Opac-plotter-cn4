#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Program upload under: GNU General Public License v3.0  - 13 Nov. 2020
# inital author: G. Rigon (LULI)

"""Programme pour le tracer des tables d'opacités et eos."""


##############################
####    Import package    ####
##############################


import tkinter as tk
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
import opacplot2 as opc
import numpy as np
from numpy import searchsorted
import pickle
from mpl_toolkits.mplot3d import Axes3D


##############################
####      Parameter       ####
##############################


mass_converter = 1.66053886e-24
var_poss = ['density','temperature','energy']

##############################
####       Fonctions      ####
##############################

class main_fenetre(object):
    """Draw the window, with the button necessary to do the plot."""

    def __init__(self):
        """Initialisation of the window, plot and button."""

        self.file_name_disp = "None"

        self.fen = tk.Tk()
        self.fen.title("EoS and Opacity plotter")

        self.E_op = tk.IntVar()
        self.E_op.trace("w", self.callback_fenLat)

        self.ion6 = tk.BooleanVar()
        self.Var_op = tk.StringVar()
        self.Var_op.trace("w", self.Clear)
        self.opac_type = tk.StringVar()
        self.opac_type.trace("w", self.Clear)

        self.can = tk.Frame(self.fen,bg='white',height=500 , width=500) #Défini un canevas(zone de dessin) dans la fenêtre
        self.can.pack(side='right') #ajuste la taille du canevas et donne sa position

        self.can_titre = tk.Label(self.can,text= "Equation of State or Opacity", font=20)
        self.can_titre.place(relx=0.5, y=20, anchor='center')

        self.list_plot_af = tk.Listbox(self.can, width= 50)
        self.list_plot = list()


        self.loading = tk.Button(self.fen, text= "Load Table", command= self.Loader)
        self.loading.pack()

        tk.Radiobutton(self.fen, text="EoS", variable=self.E_op, value=1).pack()
        tk.Radiobutton(self.fen, text="Opac", variable=self.E_op, value=2).pack()

        self.nam_table = tk.Label(self.fen, text = self.file_name_disp)
        self.nam_table.pack()


        self.help_button = tk.Button( self.fen, text="Help", command = self.helper)

        self.quit_button = tk.Button( self.fen, text= "Quit", command= self.fen.destroy)
        self.quit_button.pack(side = "bottom")
        self.help_button.pack(side = 'bottom')




        self.fen.mainloop()




    def Loader(self):
        """Fonction to load the name of the wished table, change what's written, and load the table."""
        self.file_name = askopenfilename(filetypes=[("Ionmix Tables",".cn4"),("All","*")])
        try:
            loc_fn = self.file_name.split('/')
            self.file_name_disp = loc_fn[-1]
            self.Load_table()
        except:
            a=1  # except need to exist and shouldn't be empty


    def callback_fenLat(self,*args):
        """Follow the var E_op, and change the lateral canvas depending on its new value."""
        self.Clear()
        for widg in self.can.winfo_children():
            widg.place_forget()

        if self.E_op.get() == 1:
            self.EoS_fen()
        else:
            self.Opac_fen()


    def EoS_fen(self):
        """Define the right windows /canva in the case of EoS Plotter"""

        self.can_titre = tk.Label(self.can,text= "Equation of State plotter", font=20)
        self.can_titre.place(relx=0.5, y=20, anchor='center')

        tk.Label(self.can, text= "Variable Choice:",font =18).place(relx=0.2, y=140, anchor='center')

        tk.Radiobutton(self.can, text='Density', variable= self.Var_op,\
            value="density").place(relx=0.3, y=180, anchor='center')
        tk.Radiobutton(self.can, text='Temperature', variable= self.Var_op,\
            value="temperature").place(relx=0.7, y=180, anchor='center')

        self.Plotter_block()



    def Opac_fen(self):
        """Define the right windows /canva in the case of Opac Plotter"""

        self.can_titre = tk.Label(self.can,text= "Opacity plotter", font=20)
        self.can_titre.place(relx=0.5, y=20, anchor='center')

        tk.Radiobutton(self.can, text='Rosseland', variable= self.opac_type,\
            value= "Ros").place(relx=0.2, y=90, anchor='center')
        tk.Radiobutton(self.can, text='Planck Emission', variable= self.opac_type,\
            value= "Emis").place(relx=0.5, y=90, anchor='center')
        tk.Radiobutton(self.can, text='Planck Absorbtion', variable= self.opac_type,\
            value= "Abs").place(relx=0.8, y=90, anchor='center')


        tk.Label(self.can, text= "Variable Choice:",font =18).place(relx=0.2, y=140, anchor='center')

        tk.Radiobutton(self.can, text='Density', variable= self.Var_op,\
            value="density").place(relx=0.2, y=180, anchor='center')
        tk.Radiobutton(self.can, text='Temperature', variable= self.Var_op,\
            value="temperature").place(relx=0.5, y=180, anchor='center')
        tk.Radiobutton(self.can, text='Energy', variable= self.Var_op,\
            value="energy").place(relx=0.8, y=180, anchor='center')

        self.Plotter_block()



    def Plotter_block(self):
        """Definission of the block needed for plotting.

        This is a general block fonctionning with EoS and Opac."""
# une liste + 3 boutons : add remove plot
        tk.Label(self.can, text="List to plot.", font=18).place(relx=0.2, y=240, anchor='center')

        self.list_plot_af.place(relx=0.5, y=350, anchor='center')

        tk.Button(self.can, text='Add', command=self.add_command).place(relx=0.2, y=470, anchor='center')
        tk.Button(self.can, text='Remove', command=self.Remove).place(relx=0.375, y=470, anchor='center')
        tk.Button(self.can, text='Export', command=self.Export).place(relx=0.55, y=470, anchor='center')

        if self.E_op.get()==1:
            tk.Button(self.can, text='Plot 3D', command=self.plot3D).place(relx=0.7, y=470, anchor='center')

        tk.Button(self.can, text='Plot', command=self.plot_command, fg='red').place(relx=0.85, y=470, anchor='center')

    def plot3D(self):
        T, rho= np.meshgrid(self.optable.temps, self.optable.dens)
        Pion= self.optable.pion

        f= plt.figure()
        ax= f.gca(projection='3d')

        ax.plot_surface(np.log(T), np.log10(rho), np.log10(Pion))

        ax.set_xlabel('Log Température (eV)')
        ax.set_ylabel('Log Densité (g/cc)')
        ax.set_zlabel('Log Pression (erg/cc)')
        f.show()

    def plot_command(self):
        "The plotter command."

        plt.clf()

        for i in self.list_plot:
            plt.plot(i[1], i[2], 'x-', label = i[0])

        plt.xscale('log')
        plt.yscale('log')
        plt.legend()
        plt.xlabel(self.Var_op.get())
        if self.E_op.get() == 2:
            plt.ylabel("Opacity" + self.opac_type.get() + "(cm2/g)")
        else:
            plt.ylabel("Pion (erg/cc)")

        plt.show(block= False)

    def Remove(self):
        "Remove plottable data."

        cursor = int(self.list_plot_af.curselection()[0])

        del self.list_plot[cursor]
        self.list_plot_af.delete(cursor)

    def Export(self):
        "Export data list"
        with open("out.txt", 'wb') as f: pickle.dump(self.list_plot,f)
        message_export = "Exportation down"

        fen_export = tk.Tk()
        fen_export.title("Export")

        fen_export.title("Export")
        instructions = tk.Message(fen_export, text=message_export)
        instructions.pack()

    def add_command(self):
        "Command to add a plot. Should determine the constant value"

        self.loc = ['density','temperature','energy'] # list(var_poss)
        self.loc.remove(self.Var_op.get())

        self.list_const = dict()

        if self.E_op.get() == 1:
            self.loc.remove('energy')

        self.fen_add = tk.Tk()
        self.fen_add.title("Parameter of the plot")

        for i in self.loc:
            if i =="energy":
                j = self.optable.opac_bounds[0]
                k = self.optable.opac_bounds[-1]
                l = "eV"
            elif i == "temperature":
                j = self.optable.temps[0]
                k = self.optable.temps[-1]
                l = "eV"
            else:
                j = self.optable.dens[0]
                k = self.optable.dens[-1]
                l = "g/cc"
            loc_text = "The %s span from %.2e to %.2e (%s). Which one do you want?" %(i,j,k,l)
            tk.Label(self.fen_add, text=loc_text).pack()

            self.list_const[i] = tk.Entry(self.fen_add)
            self.list_const[i].pack()

        tk.Button(self.fen_add, text='Cancel', command= self.fen_add.destroy).pack(side='left')
        tk.Button(self.fen_add, text='Confirm', command= self.ajout).pack(side='right')


    def ajout(self):
        loc_text= str()
        for i, j in self.list_const.items():
            loc_text += "   %s  =  %.2e   -" % (i, float(j.get()))

        self.list_plot_af.insert('end',loc_text)

        locplot_list = list()
        locplot_list.append(loc_text)

        if self.E_op.get() == 2:
            if self.opac_type.get() =='Ros':
                l_list =self.optable.oplRosseland()
            elif self.opac_type.get() =='Abs':
                l_list =self.optable.oplAbsorb()
            else:
                l_list =self.optable.oplEmiss()

        if self.Var_op.get() == 'energy':
            locplot_list.append(self.optable.opac_bounds[:-1])
            locplot_list.append(l_list.interp(float(self.list_const["density"].get()),\
                float(self.list_const["temperature"].get())))

        elif self.Var_op.get() == 'temperature':
            locplot_list.append(self.optable.temps)
            if self.E_op.get() == 1:
                pos = searchsorted(self.optable.dens,float(self.list_const["density"].get()))
                locplot_list.append(np.array(self.optable.pion)[pos-1])
                locplot_list[0] = loc_text+str(self.optable.dens[pos-1]) + " g/cc"
                self.list_plot.append(locplot_list)
                locplot_list = list()
                locplot_list.append(loc_text+str(self.optable.dens[pos]) + " g/cc")
                locplot_list.append(self.optable.temps)
                locplot_list.append(np.array(self.optable.pion)[pos])
                self.list_plot_af.insert('end',loc_text)
            else:
                pos = searchsorted(self.optable.opac_bounds,float(self.list_const["energy"].get()))

                l = list()
                for i in self.optable.temps:
                    a = l_list.interp(float(self.list_const["density"].get()),i)
                    l.append([a[pos-1],a[pos]])
                l = np.array(l)
                locplot_list[0] = loc_text+str(self.optable.opac_bounds[pos-1]) + "eV"
                locplot_list.append(l[:,0])
                self.list_plot.append(locplot_list)
                self.list_plot_af.insert('end',loc_text)
                locplot_list = list()
                locplot_list.append(loc_text+str(self.optable.opac_bounds[pos]) + "eV")
                locplot_list.append(self.optable.temps)
                locplot_list.append(l[:,1])


        else:
            locplot_list.append(self.optable.dens)
            if self.E_op.get() == 1:
                pos = searchsorted(self.optable.temps,float(self.list_const["temperature"].get()))
                locplot_list.append(np.array(self.optable.pion)[:,pos-1])
                locplot_list[0] = loc_text+str(self.optable.temps[pos-1]) + " eV"
                self.list_plot.append(locplot_list)
                locplot_list = list()
                locplot_list.append(loc_text+str(self.optable.temps[pos-1]) + " eV")
                locplot_list.append(self.optable.dens)
                locplot_list.append(np.array(self.optable.pion)[:,pos])
                self.list_plot_af.insert('end',loc_text)
            else:
                pos = searchsorted(self.optable.opac_bounds,float(self.list_const["energy"].get()))

                l = list()
                for i in self.optable.dens:
                    a = l_list.interp(i,float(self.list_const["temperature"].get()))
                    l.append([a[pos-1],a[pos]])
                l = np.array(l)
                locplot_list[0] = loc_text+str(self.optable.opac_bounds[pos-1]) + "eV"
                locplot_list.append(l[:,0])
                self.list_plot.append(locplot_list)
                self.list_plot_af.insert('end',loc_text)
                locplot_list = list()
                locplot_list.append(loc_text+str(self.optable.opac_bounds[pos]) + "eV")
                locplot_list.append(self.optable.dens)
                locplot_list.append(l[:,1])

        self.list_plot.append(locplot_list)

        self.fen_add.destroy()
            

    def Clear(self,*args):
        self.list_plot = list()
        self.list_plot_af.delete(0,'end')


    def Load_table(self):
        """Effectively load table, so ask for ionmix 6 and the u.a."""
        self.fen_load = tk.Tk()
        self.fen_load.title("Parameter of the table")

        tk.Label(self.fen_load, text="Some parameter are needed for loading an ionmix table.\n"\
            " Ionmix version (v4 in general):").pack()

        tk.Radiobutton(self.fen_load, text="Ionmix-4", variable=self.ion6, value=False).pack()
        tk.Radiobutton(self.fen_load, text="Ionmix-6", variable=self.ion6, value=True).pack()

        tk.Label(self.fen_load, text="Particule mass in u.a.").pack()

        self.mass = tk.Entry(self.fen_load)
        self.mass.pack()

        tk.Button(self.fen_load, text = "Validate", command = self.Loading).pack()


    def Loading(self):
        """Load table with the right parameter + change name."""
        ion6 = self.ion6.get()
        mass = self.mass.get()

        try:
            mmass= float(mass) * mass_converter
            self.optable = opc.opg_ionmix.OpacIonmix(self.file_name, mmass, man= True,\
                twot= True, hassele= ion6 ,verbose= False)
            self.fen_load.destroy()
            self.nam_table.pack_forget()
            self.nam_table = tk.Label(self.fen, text = self.file_name_disp)
            self.nam_table.pack()
        except:
            self.fen_load.destroy()
            self.Load_table()



    def helper(self):
        """Fonction displaying the help"""

        message_aide = """Not done yet.\n This program is available on https://github.com/Ielr/Opac-plotter-cn4 git repository.\n
        Please contact directly the author in case of problems."""

        fen_help = tk.Tk()
        fen_help.title("The help screen")

        fen_help.title("Aide")
        instructions = tk.Message(fen_help, text=message_aide)
        instructions.pack()


##############################
####      Programme       ####
##############################


if __name__=='__main__':
    main_fenetre()









"""
m = tk.Tk()

def callback(w,*args):
    w.pack_forget()
    if v.get()==1:
        w = tk.Label(m, text="One")
    elif v.get()==2:
        w = tk.Label(m, text="Two")
    else:
        w = tk.Label(m,text="None")
    w.pack()

v = tk.IntVar()
v.trace("w", callback)


tk.Radiobutton(m, text="Un", variable=v, value=1, command=callback).pack()
tk.Radiobutton(m, text="Deux", variable=v, value=2,command= callback).pack()



callback()



m.mainloop()



t =tk.Tk()

def simu():
    a = [1,2,3,4,5]
    plt.figure()
    plt.plot(a,a)
    plt.show(block=False)


t.title("Menu Principal")

b1=tk.Button(t,text="Lancer la simulation", command=simu)
b1.pack()
t.mainloop()


button1.pack --> canvas1.create_window(10,10,window= button1)
ou button1.place
"""
