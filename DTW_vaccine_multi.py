#!/usr/bin/env python
import os
import sys
import math

from dtaidistance.subsequence.dtw import subsequence_alignment
from dtaidistance import dtw_visualisation as dtwvis
from dtaidistance import dtw

from ont_fast5_api.fast5_interface import get_fast5_file
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
from matplotlib import rcParams
import glob
import click
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm

from itertools import repeat

import numpy as np
import numpy.testing as npt
import matplotlib.pyplot as plt


from scipy import stats
import pandas as pd
from scipy import signal

from concurrent.futures import ProcessPoolExecutor
import datetime

# major function for finding subsequence matches in raw nanopore signals
def find_sim(ref,fast5_path,verbose=True,cutoff=20000):
    # create results data.frame (pandas)
    results = pd.DataFrame(columns=['read_id','distance','startidx','endidx'])

    with get_fast5_file(fast5_path, mode="r") as f5: # open fast5

        now = datetime.datetime.now()
        print("##### processing file: " + fast5_path + "  " + str(now))
        i=0
        for read in f5.get_reads(): # iterate thorugh reads
            raw_data = read.get_raw_data(scale=True)
            raw_data = np.array(raw_data[1:cutoff]).astype(float) # get only first  {cutoff} signals
            raw_data = signal.savgol_filter(raw_data,51,3) # apply savitzky golay fiter
            raw_data = stats.zscore(raw_data) #zscore normalize signals
            read_id = read.read_id # get read_id
            # perform alignment using sequence_alignment from dtaidistance:
            seq_align = subsequence_alignment(ref,raw_data,use_c=True) #use_C - use C capabilities (faster) if compiled and available
            match = seq_align.best_match() # get best match from alignment
            startidx, endidx = match.segment # get start and end of alignment
            i=i+1
            if(endidx>startidx+10): # if start and end are not close to each other
                distance = dtw.distance_fast(ref, raw_data[startidx:endidx]) # calculate distance using fast option
                if(verbose):
                    print(str(i) + ": " + read_id + "dist: " + str(distance) + "      " + str(os.getpid()))
            else:
                distance=1000
            # add results to pandas data.frame
            temp_results = pd.DataFrame([(read_id,distance,startidx,endidx)],columns=['read_id','distance','startidx','endidx'])
            results = pd.concat([results,temp_results])
            #print(raw_data_temp)
    # output results of a given chnk to file in /tmp
    temp_output = '/tmp/' + os.path.basename(fast5_path) + '_' + str(os.getpid()) + '_DTW.tsv'
    results.to_csv(temp_output,sep="\t")
    fin_now = datetime.datetime.now()
    print("***** finished file: " + fast5_path + "  " + str(fin_now) + " (started: "  + str(now) + ")")
    return results

# get parameters with click:
@click.command()
@click.option('--inpath', '-i', help='The input fast5 directory path')
@click.option('--ref_signal', '-r', help='reference signal')
@click.option('--output', '-o', help='output file')
@click.option('--threads', '-t', default=1, help='parallel threads to use')
@click.option('--verbose', '-v', is_flag=True, default=False, help='Be verbose?')

def main(inpath,ref_signal,output,threads,verbose):

    # load reference signal
    ref_sig = np.loadtxt(ref_signal,dtype="float")
    ref_sig = ref_sig[1:5000].astype(float) # get only first 5000 signal points
    ref_sig = signal.savgol_filter(ref_sig,51,3) # apply savitzky golay fiter
    ref_sig = stats.zscore(ref_sig) #zscore normalize signals
    print("Succesfully read reference signal")

    fin_results = pd.DataFrame(columns=['read_id','distance','startidx','endidx']) # create pandas data.rame for results

    futures = [] # initialize futures

    # get fast5 files from input path
    files = []
    for fileNM in glob.glob(inpath + '/**/*.fast5',recursive=True):
        #print(fileNM)
        files.append(fileNM)


        # start processes pool (futures)
    with ProcessPoolExecutor(max_workers=threads) as pool:
        results = list(pool.map(find_sim, repeat(ref_sig), files, repeat(verbose)))

    # produce and save final results
    fin_results = pd.concat(results)
    fin_results.to_csv(output,sep="\t")

if __name__ == '__main__':
    main()
