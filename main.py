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
    for key1, val1 in massive.items():
        for key2, val2 in val1.items():
            print(key2, "key2")
            print(val2, "val2")
            '''if 'NMR Status' in key2:
                x = val2
            if x '''
            if 'NMR Data' not in key2:
                non_nmr[key2] = val2
            elif 'NMR Data' in key2:
                nmr_data_dict[key1] = val2
            else: 
                continue
        print(non_nmr)
        print(nmr_data_dict)
        exit()
    print(non_nmr)
    #print(nmr_data_dict)
    non_nmr_df = pd.Series(non_nmr) #This should be a DF, didn't like no index being called tho          
    #Successfully split into two, combine into a dictionary or DF?
    return non_nmr_df, nmr_data_dict
# how to get integer from dataframe for frequency centroid and span
# how to get rand_data to stop saying not referenced (dummy)
# average sweeps?

                 
#want to break up df of NMR sweeps by continuous runs of the same type
def seperate_runs(massive, nmr_data_dict, runtype):
    x = []
    for key1, val1 in massive.items():
        #Value Error here
        for key2, val2 in val1.items():
            if 'NMR Status' in key2:
                x.append(val2)
    for val in x:
        #print(val, x.index(val))
        if val == '---':
            null_inds = x.index(val)
        elif val == 'Baseline':
            BL_inds = x.index(val)
        elif val == 'TE':
            TE_inds = x.index(val)
        elif val == 'Polarization':
            PL_inds = x.index(val)
    #print(BL_inds)
    return True
#
    BL_data = {}
    if runtype == 'Baseline':
        for key, val in nmr_data_dict.items():
            if x.index(val) not in BL_inds:
                continue
            elif x.index(val) in BL_inds: 
                BL_data[key]=val
    #print(BL_data)            
    ###attempting to find row indeces of continuous runs of same types, then snip those indeces out to make run-type DFs of data    
    #would it be ok to keep the run-type with the NMR data and strip later after seperating them by runtype? would then be able to use the seperation functions below
    #is it ok to make the runtype a variable in function, or should i make multiple functions
    return            

def clean_na(dirtydf):
    #remove any rows with ---, null readings
    #check to see if something went wrong and value is nonetype
    print(dirtydf is None)
    cleandf = dirtydf.drop(dirtydf[dirtydf["NMR Status"]=='---'].index)
    return cleandf

def seperateBL(cleandf):
    #add values to different sets based on NMR status column
    BL_df = pd.DataFrame(cleandf.loc[cleandf['NMR Status']=='Baseline'])
    return BL_df

def seperateTE(cleandf):
    TE_df = pd.DataFrame(cleandf.loc[cleandf['NMR Status']=='TE'])
    return TE_df

def seperatePL(cleandf):
    PL_df = pd.DataFrame(cleandf.loc[cleandf['NMR Status']=='Polarization'])
    return PL_df

dirtydata = load()
assigned = assigninds(dirtydata)

non_nmr_df, nmr_data_dict = break_ups(assigned) 
BL_runs = seperate_runs(assigned, nmr_data_dict, 'Baseline')