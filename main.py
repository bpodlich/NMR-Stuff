# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 10:28:19 2022

@author: benpo
"""

import math
import numpy as np
import matplotlib.pylab as plt
import pandas as pd
from scipy.optimize import curve_fit
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
                inner[key] = np.asarray(listed_line[ind:],dtype = float)
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
    nmr_data = {}

    #
    #### "Massive dictonary[timestamp] = {stuff we want : stuff, NMR_DATA:nmr_data}
    #take all timestamps from massive
    times = [k for k in massive]
    #
    #iterate thru times, pop to lessen values to iterate
    for t in times:
        row = massive.pop(t)
        non_nmr_t = {}
        #get keys of massive dictionary item(row/sweep)
        ks = [k for k in row]
        for key in ks:
            if "NMR Data" not in key:
                non_nmr_t[key] = row.pop(key)
            else:
                continue
        
        non_nmr[t] = non_nmr_t
        #do central frequency and span, turn into x axis around here
        
        
        nmr_data[t] = pd.DataFrame(row)
    #print(nmr_data)
    #print(non_nmr)
    return nmr_data, non_nmr
            
#want to break up df of NMR sweeps by continuous runs of the same type
def seperate_runs(nmr_data, non_nmr):
    
    runs_dict = {}

    #print(nmr_data)
    #print(non_nmr)
    
    non_nmr_df = pd.DataFrame.from_dict({(i):non_nmr[i]
                                         for i in non_nmr.keys()},
                                        orient = 'index').reset_index()
    
    #print(non_nmr_df)

    #find changes of status, find those row indexes, build nested list of consec run indeces.
    changes_ind = non_nmr_df[non_nmr_df['NMR Status'].shift() != non_nmr_df['NMR Status']].index.to_list()
    #print(changes_ind)
    
    #nested list of consec indeces
    list_consecs = []
    list_1_type = []
    length = len(changes_ind)
    #print(length)
    for ind, val in enumerate(changes_ind):
        next_ind = ind +1
        if next_ind < length:   
            list_1_type = [val, changes_ind[next_ind]-1]
        if next_ind >= length:
            list_1_type = [val, len(non_nmr)]
        list_consecs.append(list_1_type)
    #print(list_consecs)
    
    #empty string for type and full name, empty count vars for each type of run
    name = ''
    cont_list = []
    bl_list = []
    #using run count instead of i to track runs bc i will be +1 if we boot out a singular sweep run
    run_count = 0
    for i, (start,finish) in enumerate(list_consecs):
        
        one_run_dict = {}
        subsect = non_nmr_df.iloc[start:finish+1] #i think this doesn't output a answer for the [139,139] tuple is that ok?
        #the +1 above fixes all non_output issues
        #print(subsect)
        count_row = subsect.shape[0]
        run_count +=1
        #this boots out any singular runs without similar runs next to it
        if count_row >1:
            name = subsect.iloc[0]['NMR Status'] # to keep the [139, 139] tuple from messing this up
        else:
            run_count -=1
            continue
        #this appends bl list if status = bl
        if name == 'Baseline':
            bl_list.append(run_count)
            cont_list.append(run_count) #for if bl run numbers should be included in continua list
            
        else:
            cont_list.append(run_count)
                
        
        #open empty dict for data frames of a sweeps data to its time stamp
        sub_times = {}
        
        #determine central and freq span in order to add x axis data to dataframes
        
        span = float(subsect.iloc[0]['Freq Span (MHz)'])
        center = float(subsect.iloc[0]['Central Freq (MHz)'])
        
        first_sweep = subsect.iloc[0]['Time']
        data_pts = len(nmr_data[first_sweep])

        step = span/data_pts
        low = center - (span/2) 
        high = center + (span/2) #to include last data pt, should i add another step? makes there be +1 freq than sweep data pts.
        
        freq_array = np.arange(low, high, step)
        freaks = freq_array.tolist()
        
        
        #print(len(freaks))
        
        for time in subsect['Time']:
            #print(time)
            #print(data)
            sweep_df = nmr_data.pop(time) # Grab NMR DATA From big nmr dict
            
            sweep_df['Frequency (MHz)'] = freaks # Assign x-axis to NMR dict entry
            
            sub_times[time]=sweep_df # Subsection of NMR data for specific run
            
        #sub_times['Frequency'] = freaks # in case we want one freq list per run 
        #print(sub_times) #dictionary of nmr and freq data keyed to time
        
        #combine non-nmr and nmr-data into one dict per run
        one_run_dict['Info'] = subsect # this puts the entire non_nmr df into this value for key 'info', I think I only want one row of info
        one_run_dict['Sweeps'] = sub_times
        
        run_name = 'Run #' + str(run_count)
        #print(run_name)
        runs_dict[run_name] = one_run_dict
        
        
        
        

    #print(cont_list)
    #print(bl_list)
    #print(runs_dict.keys()) # this shows keys for massive dict are correct
    #print(runs_dict['Run #2']['Info'])#this is only displaying run #5's data in each run's info thingy  and sweeps? not iterating? or not saving each iteration?
        
        #massive_dict[]
        #for i in range(subsect.shape[0]):#need to now assign nmr data to each subsection by timestamps
        # make a dict of Time stamp : One sweep's data, assign to dict of Sweep Info: earlier dict, assign to the correct run # and type
            #one_run_dict[]
        
            #I appear to still have NMR Status in nmr_data_dict
            
    return runs_dict, cont_list, bl_list, list_consecs


# main goal of averaging BL data
def BLavg(runs_dict, bl_list, cont_inds):
    
    
    #make list of column names w numeric data
    num_signs = ['(MHz)', '(K)']
    
    #iterate thru list of bl runs
    for bl in bl_list:
        #open and reset seperate empty dataframes for numeric and non numeric non_nmr data
        non_num_info = pd.DataFrame()
        num_info = pd.DataFrame()
        #take run # from bl_list, make into form of a massive_dict key(ie Run #1)
        call_sign = 'Run #' + str(bl)
        run_info = runs_dict [call_sign]['Info']
        #iterate thru headers of non_nmr data, match numeric data to numeric info df
        for k in run_info:
            if any(match.lower() in k.lower() for match in num_signs):
                num_info[k] = run_info[k].astype(float)
                #print(num_info[k])
            else:
                non_num_info[k] = run_info[k]
                #print(non_num_info)       
        #mean the numeric info, reset and transpose to get into nice row of data
        mean_info = num_info.mean().reset_index().transpose()
        #set column names to info headers
        fix = mean_info.rename(columns = mean_info.iloc[0])
        mean_info = pd.DataFrame(fix.values[1:], columns = fix.iloc[0])
        #find end index of that baseline to compare against non_bl indeces for subtraction
        end_bl_ind = cont_inds[bl-1][-1]
        non_num = non_num_info.iloc[-1]
        
        nN = non_num.reset_index().transpose()
        non_num = pd.DataFrame(nN.values[1:],columns = nN.iloc[0])
        info = pd.concat([mean_info, non_num], axis = 1)
        info['index']=end_bl_ind
        info = info.set_index('index')
        runs_dict[call_sign]['Info'] = info
        #print(runs_dict['Run #3']['Info'])
        #done averaging non_nmr info, 
        #start averaging BL nmr data
        
        
        #call the nmr data section of massive dict
        run_data = runs_dict[call_sign]['Sweeps']
        #print(list(run_data.keys()))
        #print(run_data)
        #open empty df for NMR data only, dont need to bring and average frequency data
        run_df = pd.DataFrame()
        #lets split the MHz and NMR data
        x = 'Frequency (MHz)'
        y = 'NMR Data'
        t = run_info['Time'].to_list()
        for i,(_,data) in enumerate(run_data.items()):
            if i == 0:
                #print(data)
                #set up length of data measure
                l = len(data[x])
                X=data[x].to_numpy(dtype=float)
                Y = data[y].to_numpy(dtype = float)
            try:
                X = X + data[x].to_numpy(dtype= float)
                Y = Y + data[y].to_numpy(dtype = float)
            except ValueError:
                continue
        l = len(run_data)
        run_df[x] = X/l
        run_df[y] = Y/l
        #empty old NMR data
        runs_dict[call_sign]['Sweeps'] = {}
        #add new averaged nmr data in its place with last timestamp in run as key value
        runs_dict[call_sign]['Sweeps'] [t[-1]]= run_df
        #print(runs_dict[call_sign]['Sweeps'])

        
#this will return the run_dict with non_bl runs untouched, bl runs averaged info with last ind of bl sweeps         
    return runs_dict            
            
def BL_sub(runs_dict, cont_list, bl_list):
    #want to subtract each sweeps nmr data from the last baseline's averaged data 
    y = 'NMR Data'
    x = 'Frequency (MHz)'
    #print(cont_list)
    #print(bl_list)
    #print(len(bl_list))
    continua_ranges = []
    for i,bl in enumerate(bl_list):
        #print(i)
        if i+1 < len(bl_list):
            last_of = bl_list[i+1] -1
        if i+1 >= len(bl_list):
            last_of = cont_list[-1]   
        continua_ranges.append([bl,last_of])

    #print(continua_ranges) # this shows a nested list of [[BL,last to sub from that BL,[BL, last...]]]
    
    

    #iterate through continua indeces, subtract nearest bl 
    for run in cont_list:
        
        call_sign = 'Run #' + str(run)
        if run in bl_list:  # if the run is a bl, skip
            continue
        
        for i,cont in enumerate(continua_ranges):
            #split range into BL, last to sub from that BL
            bl = cont[0]
            last = cont[1]
            
            #dict of timestamp: baseline sweep dataframes
            bl_data = runs_dict['Run #'+str(bl)]['Sweeps']#['NMR Data']
            #print(bl_data)
            
            #ensure that only nearest bl is subtracted from
            if bl > run: 
                continue
            if run > last:
                continue
            if  bl < run <= last:
                run_data = runs_dict[call_sign]['Sweeps']
                
            #ite through non_bl sweep data  
            for t,data in run_data.items():
                #put sweep data and avg bl into numpy array to subtract from each other
                sweep_data = data[y].to_numpy() #
                #print(sweep_data)
                freq_data = data[x].to_numpy()
                avg_bl_data = (list(bl_data.items())[0][1])[y].to_numpy() #list of nearest bl NMR data only(no freqs), put into array
                #print(avg_bl_data)
                #return False
                
                
                # subtract non_bl sweep array from avg_bl sweep array
                subt_array = np.subtract(sweep_data, avg_bl_data)
                
                
                run_subt_df = pd.DataFrame()
                run_subt_df[x] = freq_data
                run_subt_df[y] = sweep_data
                run_subt_df['Baseline'] = avg_bl_data
                run_subt_df[y+' Baseline Subtracted'] = subt_array 
                #print(run_subt_df)
                
                runs_dict[call_sign]['Sweeps'][t] = pd.DataFrame()
                runs_dict[call_sign]['Sweeps'][t] = run_subt_df
                
    #print(runs_dict['Run #4']['Sweeps'])            
                               
    return runs_dict

#fit to subtract bl_subt from
def cube_fit(x,a,b,c,d):
    fit = a*x**3+b*x**2+c*x+d
    return fit

#ensure freq span and centroid dont change at all in the data file, otherwise raise alarm
#def validate(runs_dict):
    #lol dont do this 

#define fit line with the wings of data, subtract bl_sub data, use ginput to click on graph to refit wings, re subtract data from new fit line 
def fit_sub(runs_dict, cont_list, bl_list):
    #print(runs_dict.keys())
    #ite thru all non bl runs
    for i,num in enumerate(bl_list):
        bl_list[i] = "Run #" + str(num)
        
    for run in runs_dict.keys():
        #dont want to do fit subtraction on bl runs, only bl-subtracted sweeps
        if run in bl_list:
            continue
        else:
            print(run)
            for i,(t,data) in enumerate(runs_dict[run]['Sweeps'].items()):
                #take 15% of data from front and back to fit with
                slizity = int(len(data)*.15)
                front_slice = data.iloc[:slizity][:]
                back_ind = len(data)-slizity
                back_slice = data.iloc[back_ind:][:]
                
                wings = pd.concat([front_slice,back_slice]) #external ends of data, certain to be almost only bl, no physics
                print(wings)
                
                #now define curve fit
                #check wing shape
                x = wings['Frequency (MHz)']
                y = wings['NMR Data Baseline Subtracted']
                #BL_subd_plot = plt.plot(x, y , '*')
                #plt.show()
                #PROBLEM : AB 1/2 OF WINGS ARE OF WRONG SHAPE
        
    return


class DataHandler(object):
    def __init__(self, run_df, **kwargs):
        self.run_df = run_df


dirtydata = load()
assigned = assigninds(dirtydata)

nmr_data_dict, non_nmr_df = break_ups(assigned) 
massive_dict, continua_lst, bl_lst, continua_inds = seperate_runs(nmr_data_dict, non_nmr_df)
bl_avgd_massive = BLavg(massive_dict,bl_lst,continua_inds)
bl_subd_massive = BL_sub(bl_avgd_massive,continua_lst,bl_lst)

fit_subd = fit_sub(bl_subd_massive,continua_lst,bl_lst)
