#!/usr/bin/env python
import os
import sys
import traceback

sys.path.append('/usr/local/software/libraries/python/diaidistance/2.3.6/lib/python3.8/site-packages/')
import glob
import click
import numpy as np

sys.path.append('/usr/local/software/ont-fast5-api/4.0.0/lib/python3.8/site-packages/')
from ont_fast5_api.fast5_interface import get_fast5_file
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'



sys.path.append('/usr/local/software/libraries/python/pandas/1.4.0/lib/python3.8/site-packages/')

import pandas as pd




@click.command()
@click.option('--infile', '-i', help='Input fast5 file')
@click.option('--read_id', '-r', help='Read ID')
@click.option('--nanopolish', '-n', help='nanopolish file')
@click.option('--output', '-o', help='output file')


def main(infile,read_id,nanopolish,output):


    nanopolish_output=pd.read_csv(nanopolish,delimiter="\t")
    #test=nanopolish_output[nanopolish_output["readname"]=='0000c3a7-3bf9-4429-b8c5-e6eea14416da']["transcript_start"].iat[0]

    f5=get_fast5_file(infile, mode="r")
    read=f5.get_read(read_id)
    raw_data = read.get_raw_data(scale=True)
    print(read.read_id)
    print(raw_data)
    correct_read=1
    try:
        transcript_start=int(nanopolish_output[nanopolish_output["readname"]==read.read_id]["transcript_start"].iat[0])
    except:
        print("error")
        correct_read=0
    if(correct_read==1):
        #print(transcript_start)
        raw_data2=raw_data[transcript_start-1000:]
        #print(raw_data2)

        np.savetxt(X=raw_data2,fname=output,fmt="%d")

if __name__ == '__main__':
    main()
