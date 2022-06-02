#!/usr/bin/python3

from datetime import datetime
import os
import numpy as np
import sys


def make_list(path,ldate,tpath=''):

    if len(tpath) == 0:
        tpath = path
    atmo = []
    cold = []
    bb = []
    hot = []

    #scold = 'sr80'
    #scold = 'rt'
    scold = 'ht_0'
    #scold = 'bb_20.0'
    #shot = 'ir301'
    #shot = 'ht1'
    #shot = 'bb_100.0'
    ssky = 'roof'
    # ssky = 'up'
    # ssky = 'ir301'
    #scold = 'sr800_20.0'
    shot = 'sr800_120.0'
    scold2 = 'sr800_19.9'
    shot2 = 'sr800_119.9'
    #spec_dir = os.path.join(path,'Emission',ldate)
    spec_dir = os.path.join(path,ldate)
    if not os.path.exists(spec_dir):
        print('Sirectory {} does not exist'.format(spec_dir))
        return(-1)
    files = os.listdir(spec_dir)
    lfile = '{}{}'.format(ldate,'.list')
    
    fid = open(lfile,'w')
    for ff in files:
        if ff.find('_%s'%scold) > -1 or ff.find('_%s'%scold2) > -1:
            cold.append([ff, datetime.strptime(ff[4:18],'%Y%m%d%H%M%S'),20])
            cold.sort()
        if ff.find('_%s'%shot) > -1 or ff.find('_%s'%shot2) > -1:
            hot.append([ff,datetime.strptime(ff[4:18],'%Y%m%d%H%M%S'),110])
            hot.sort()
        if ff.find('_%s'%ssky) > -1:
            atmo.append([ff,datetime.strptime(ff[4:18],'%Y%m%d%H%M%S')])
            atmo.sort()

    td = lambda x: datetime.strptime(path+' '+x, '%Y%m%d %H:%M:%S')
    
    ht1 = []
    rt = []
    dnum1 = []

    if False:
        with open(os.path.join(path,'Emission','tlogs',ldate+'_bb_targets.dat')) as tfid:
            for ll in tfid:
                en = ll.split()
                if len(en)<11:
                    continue
                try:
                    dnum1.append(td(en[1]))
                except:
                    continue
                ht1.append(np.mean(list(map(float,en[2:5]))))
                rt.append(np.mean(list(map(float,en[7:10]))))

    sr80 = []
    dnum2 = []
    td = lambda x: datetime.strptime(x, '%Y%m%d %H:%M:%S')
    if False:
        tfid = open(path+'tlogs/'+ldate+'_sr80_targets.dat')
        tfid.seek(0)
        for i in range(0,7):
            tfid.readline()
        for ll in tfid:
            en = ll.split()
            #            try:
            sr80.append([en[2], td(en[0]+' '+en[1])])
            #            except:
            #                continue
            
        tfid.close()
    if scold == 'sr80':
        for cind in range(0,len(sr80)):
            ind = np.where(sr80[cind][1] == np.array(cold)[:,1])
            if ind[0].size>0:
                i = ind[0][0]
                print(cold[i], sr80[cind][0])
                cold[i][2] = sr80[cind][0]
                fid.write('{}\n'.format(len(atmo)))
    fid.write('{}\n'.format(len(atmo)))
    for at in atmo:
	# find nearest cold spectrum
        print(at)
        ic = np.argmin(np.abs(at[1] - np.array(cold)[:,1]))
        # find nearest hot spectrum
        ih = np.argmin(np.abs(at[1] - np.array(hot)[:,1]))
        # create name of final spectrum
        final = '{}{}{}'.format(at[0].split('_')[0],'_FINAL.',at[0].split('.')[-1])
        if tpath.find('\\'):
            sep = r'\\'
        else:
            sep = '/'
        fid.write('{:<100}{:<50}{:<50}{:<50}{:<50}{:<10}{:<10}\n'.format(sep.join((tpath,'Emission',ldate)),hot[ih][0],cold[ic][0], at[0], final, float(hot[ih][2]) + 273.15, float(cold[ic][2]) + 273.15))

    fid.close()
    return(lfile)

if __name__ == '__main__':

    #path = '/home/mathias/Vertex80_spectren/20190829'

    path = sys.argv[1]
    ldate = sys.argv[2]
    if len(sys.argv) == 4:
        make_list(path, ldate, sys.argv[3])
    elif len(sys.argv) == 3:
        make_list(path, ldate)
    else:
        print('Call as python3 make_list.py path date(YYYYMMDD) [path in other system]')
    

