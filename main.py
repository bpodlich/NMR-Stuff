import math
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
from pathlib import Path  # pathlib.Path formats pathnames to suit your operating system

# "notebook" plotting mode allows for interactive (zoom-able) plots, "inline" doesn't 
# %matplotlib inline

#function to load the datafile
# find and parse data into baseline , null, TE , and Polarized
def load(filename = 'test_data.csv'):
    #return pd.read_csv(filename, index_col=[0])
    with open(filename, 'r') as f:
        return f.read()
    
#want to assign header names to a dictionary's keys, then use line>0 to fill a dictionary with a sweeps values
def assigninds(f):
    line_by = f.split('\n')
    len_line_by = len(line_by)
    #make empty dict for header names as keys
    header_dict = {}
    #make empty dict of dicts for individual sweeps
    massive_dict = {}
    #CELLS TO KEEP
    keepers = ['.T2 (K)', '.T1 (K)', '.T3 (K)', '.F10 (K)', '.F11 (K)',
               "Vapor Pressure Temperature (K)", 'NMR Data', 'Time', 'Freq Span (MHz)', 'Central Freq (MHz)', 'NMR Status']#****
    for i,line in enumerate(line_by):
       #########################################
        listed_line = line.split(',')
        if i == 0:
            for ind,cell in enumerate(listed_line):#****
                # throw an if statement in here with any to fill header_dict with keeper headers and indeces
                if any(match.lower() in cell.lower() for match in keepers):
                    header_dict[cell] = ind
                    #########################################
            continue
        elif len(listed_line) < len(keepers):
            # Resolves index error on line 48 for EOF
            break
        #inner is dummy for dict to enter into massive
        inner = {}
        #for loop through interesting headers
        for key in header_dict:
            #get ind for interesting header in question
            ind = header_dict[key]
            # split off the NMR data into one value for inner dict
            if "NMR Data" not in key:
                inner[key] = listed_line[ind]
                    
            elif "NMR Data" in key:
                inner[key] = listed_line[ind:]
            else:
                continue
        #when in doubt, print it out
        #print(header_dict["Time"])
        #print([listed_line[header_dict["Time"]]])
        #print(inner)
        
        massive_dict[listed_line[header_dict["Time"]]] = inner
        # to call a value in the 2-d dict (for seperations), use like massive_dict [timestamp][run-type]    
        # want to seperate continuous stretches of the same type of run, and stores them by themselves in a dictionary of  DFS
        # accomplish this by seperating all non-NMR data into a single big DF, and all the NMR data into individual DFs by sweep in a dict with key = timestamp
    #print a section of massive dict to check
    #print(header_dict)
    #print(massive_dict)
    return massive_dict

#want to break up massive dictionary into 1 DF of non-nmr shit, one dict of n key-vals for NMR data
def break_ups(massive):
    non_nmr = {}
    nmr_data_dict = {}

    #
    #### "Massive dictonary[timestamp] = {stuff we want : stuff, NMR_DATA:nmr_data}

    times = massive.keys()

    for t in times:
        row = massive.pop(t)
        non_nmr_t = {}

        ks = row.keys()
        for key in ks:
            if "NMR Data" not in key:
                non_nmr_t[key] = row[key]
            else:
                continue
        nmr_data_dict[t] = pd.DataFrame(row)
        non_nmr[t] = non_nmr_t

    return nmr_data_dict, non_nmr
                 
#want to break up df of NMR sweeps by continuous runs of the same type
def seperate_runs(nmr_data_dict, non_nmr):
    run_dict = {}

    """
    1) Turn the non_nmr nested dictionary into a dataframe, using the keys of non_nmr as the index of the dataframe
        non_nmr[timestamp] = {non nmr data}

    2) find changes of state with df[df["NMR Status"].shift()!=df["NMR Status"]].index.to_list

    3) Find a way to create a list of tuples as I did from the changes of state that you detected from
        step 2
        [a, b, c, d, e, f, g, ..., n] -> [[a,b-1], [b, c-1], [c,c-1] ... ]

    4) Using the list of tuples generated in step 3, create your run-seperated dictionary.

    """
    return run_dict
    #
    #print(BL_data)            
    ###attempting to find row indeces of continuous runs of same types, then snip those indeces out to make run-type DFs of data    
    #would it be ok to keep the run-type with the NMR data and strip later after seperating them by runtype? would then be able to use the seperation functions below
    #is it ok to make the runtype a variable in function, or should i make multiple functions
    return

class DataHandler(object):
    def __init__(self, run_df, **kwargs):
        self.run_df = run_df






dirtydata = load()
assigned = assigninds(dirtydata)

non_nmr_df, nmr_data_dict = break_ups(assigned) 
BL_runs = seperate_runs(assigned, nmr_data_dict, 'Baseline')
