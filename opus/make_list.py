#!/usr/bin/python3

from datetime import datetime
import os
import numpy as np
import sys


def make_list(path):

    files = os.listdir(path) 

    atmo = []
    cold = []
    bb = []
    hot = []

    # Construct name of list file
    lfile = '{}{}'.format(path.split(os.path.sep)[-1],'.list')
    
    fid = open(lfile,'w')
    for ff in files:
        if ff.find('bb_20.0') > -1:
            cold.append([ff, datetime.strptime(ff[4:18],'%Y%m%d%H%M%S')])
            cold.sort()
        if ff.find('bb_100.0') > -1:
            hot.append([ff,datetime.strptime(ff[4:18],'%Y%m%d%H%M%S')])
            hot.sort()
        if ff.find('_up.') > -1:
            atmo.append([ff,datetime.strptime(ff[4:18],'%Y%m%d%H%M%S')])
            atmo.sort()


    fid.write('{}\n'.format(len(atmo)))
    for at in atmo:
        # find nearest cold spectrum
        ic = np.argmin(np.abs(at[1] - np.array(cold)[:,1]))
        # find nearest hot spectrum
        ih = np.argmin(np.abs(at[1] - np.array(hot)[:,1]))
        # create name of final spectrum
        final = '{}{}{}'.format(at[0].split('_')[0],'_FINAL.',at[0].split('.')[-1])
        fid.write('{:<100}{:<50}{:<50}{:<50}{:<50}{:<10}{:<10}\n'.format(path,hot[ih][0],cold[ih][0], at[0], final, 373.15, 293.15))

    fid.close()

if __name__ == '__main__':

    #path = '/home/mathias/Vertex80_spectren/20190829'

    path = sys.argv[1]
    if len(sys.argv) == 2:
        make_list(path)
    else:
        print('Call as python3 make_list.py path')
    

