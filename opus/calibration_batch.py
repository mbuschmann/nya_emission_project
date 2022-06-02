#! /usr/bin/python

# batch to create spectralist and run opus macro on this list.

# batch to create spectralist and run opus macro on this list.

from opusPipe import OPUSpipe
from ckOPUS import ckOPUS
from time import sleep
from datetime import datetime, timedelta,date
from matplotlib.dates import drange, num2date, datestr2num
from shutil import copy
from make_list_denghui import make_list
import os


def run_opus_batch(s_date = 0, e_date = 0):
        # s_date and e_date are datenums
        
        if s_date == 0 or e_date == 0:
                s_date = datetime.today()-timedelta(days=1)
                e_date = s_date + timedelta(days=1)
        else:
                s_date = num2date(s_date)
                e_date = num2date(e_date)
                e_date = e_date + timedelta(days=1)
        print(s_date, e_date)
        spec_path = r'z:\out'
        list_dir = r"z:\out"


        for aktdate in drange(s_date,e_date,timedelta(days=1)):
                ifile = make_list(spec_path, num2date(aktdate).strftime('%Y%m%d'),'1')
                if ifile == -1:
                        print('path {} does not exist'.format(ifile))
                        continue
                ifile = os.path.abspath(os.path.join(os.path.curdir, ifile))
                print(ifile)
                
                inp_file = r"{}".format(ifile)

                out_dir =  "z:\\out\\Emission"
                mtxfile = r"c:\Users\ftir\nya_emission_project\opus\hot_cold_from_list.mtx"

                cmdstring = r"START_MACRO {} 2\n".format(mtxfile)
                argstring = "{0:}\n{1:}\n".format(inp_file, out_dir)
                ckOPUS(overRideRestart=True)
                
                op = OPUSpipe()
                sleep(10)
                op.connectPIPE()
                sleep(10)
                print(cmdstring)
                op.writePIPE(cmdstring)
                print(op.readPIPE())
                print(argstring)
                op.writePIPE(argstring)
                print(op.readPIPE())

if __name__ == '__main__':
        import sys
        if len(sys.argv) == 1:
                run_opus_batch()
        elif len(sys.argv) == 3:
                run_opus_batch(datestr2num(sys.argv[1]), datestr2num(sys.argv[2]))
        else:
                print ('Either no or two arguments (startdate and endate) of the form YYYMMDD')
                
