# Opac-plotter-cn4
A short python gui-based programm to help visualizing opacity and EoS as used in FLASH4 (cn4 format)

This program is written in python and need some dependancies.

The usual distribution one are:
tkinter, matplotlib, numpy, pickle

A git based repository: opacplot2.

```shell
pip3 install git+https://github.com/flash-center/opacplot2
```

# Usage
Just launch the scipt as follow:

```shell
python3 ploter.py
```

or with ipython3.

Usage is quite self-explenatory: on the gui use load to load a ".cn4" file, choose the write format (usually INOMIX4) and give the molecule mass in u.a.

The program allows to plot the EoS and Opacity (Rosseland, Planck emission and absorption). After choosing what to plot choose the variable and click the 
"add" button. You will be prompt for the value of the fixed variable (the non choosen variable). 2 curves will then be generated for the nearest tabulated value. 
They can be visualized with plot.
