#! /usr/bin/python2.7

from opusPipe import OPUSpipe
from ckOPUS import ckOPUS
from datetime import datetime, timedelta
from matplotlib.dates import drange, num2date
from shutil import copy
from make_list import make_list
import os


def run_opus_batch(s_date = 0, e_date = 0):

	if s_date == 0 or e_date == 0:	      
		s_date = datetime.today()-timedelta(days=1)
		e_date = s_date + timedelta(days=1)

	spec_path = r'x:\Vertex80_NyAlesund'
	list_dir = r"y:\\Vertex80_NyAlesund"

	for aktdate in drange(s_date,e_date,timedelta(days=1)):
		ifile = make_list(spec_path, num2date(aktdate).strftime('%Y%m%d'))
		if ifile == -1:
			print('path {} does not exist'.format(ifile))
			return()
		ifile = os.path.abspath(os.path.join(os.path.curdir, ifile))
		print(ifile)
		
		inp_file = r"{}".format(ifile)
		out_dir =  "y:\\\\Vertex80_NyAlesund\\Emission"
		mtxfile = r"z:\projects\nya_emission_project\opus\hot_cold_from_list.mtx"
		cmdstring = r"START_MACRO {} 2\n".format(mtxfile)
		argstring = "{0:}\n{1:}\n".format(inp_file, out_dir)
		ckOPUS(overRideRestart=True)
		op = OPUSpipe()
		op.connectPIPE()
		print(cmdstring)
		op.writePIPE(cmdstring)
		print(op.readPIPE())
		print(argstring)
		op.writePIPE(argstring)
		print(op.readPIPE())

if __name__ == '__main__':
	if len(sys.argv) == 0:
		run_opus_batch()
	elif len(sys.argv == 2):
		run_opus_batch(sys.argv[1], sys.argv[2])
	else:
		print ('Either no or two arguments (startdate and endate) of the form YYYMMDD)
		
