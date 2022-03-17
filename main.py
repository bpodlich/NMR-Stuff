import math
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
from pathlib import Path  # pathlib.Path formats pathnames to suit your operating system

# "notebook" plotting mode allows for interactive (zoom-able) plots, "inline" doesn't
%matplotlib notebook   
# %matplotlib inline

#function to load the datafile
# find and parse data into baseline , null, TE , and Polarized
def load(filename = 'test_data.csv'):
    #return pd.read_csv(filename, index_col=[0])
    with open(filename, 'r') as f:
        return f.read()
    
#want to assign header names to a dictionary's keys, then use line>0 to fill a dictionary with a sweeps values
def assigninds(f):
    print(f)
    #make empty dict for header names as keys
    header_dict = {}
    #make empty dict of dicts for individual sweeps
    massive_dict = {}
    
    #CELLS TO KEEP
    keepers = ['.T2 (K)', '.T1 (K)', '.T3 (K)', '.F10 (K)', '.F11 (K)', "Vapor Pressure Temperature (K)", 'NMR Data']#****
    for i,line in enumerate(f):
        if i == 0:
            print(line)
            for ind,cell in enumerate(line.split(',')):#****
                # throw an if statement in here with any to fill header_dict with keeper headers and indeces
                if any(match.lower() in cell.lower() for match in keepers):
                    header_dict[cell] = ind
                    
            continue
                #now have dictionary with column headers as keys, index as value
                #find index of start of NMR data, frequency readings
                
                
            #start_data_col = header_dict['NMR Data']
            #freq_cent_col = header_dict['Central Freq (MHz)']
            #freq_span_col = header_dict['Freq Span (MHz)']
            #freq_cent = f.iloc[2:3,freq_cent_col:freq_cent_col+1]
            #freq_span = f.iloc[2:3,freq_span_col:freq_span_col+1] 
    print(header_dict)
    return True
    #print(freq_cent)
        #want to go to each row, parse the data from each column into a new dictionary with headers and values, add that to big dictionary
    length = len(f.index)
    print(length)
    """if 0 < i < length:
        rand_data = f.iloc[i:i+1,:start_data_col]
        NMR_data = f.iloc[i:i+1,start_data_col:]
        #this was working but only going to the 483 row, now is saying variables not referenced ??
    print(rand_data)
    print(NMR_data)"""
        
            
# how to get integer from dataframe for frequency centroid and span
# how to get rand_data to stop saying not referenced (dummy)
# average sweeps?

                 

      
                

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

