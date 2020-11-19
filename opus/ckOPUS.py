#! c:\Python27\python
#----------------------------------------------------------------------------------------
# Name:
#        ckOPUS.py
#
# Purpose:
#       Program checks to see if multiple versions of OPUS are running and if pipes are
#       present. If not start new version of OPUS
#
#
#
# Notes:
#
#
# License:
#    Copyright (c) 2013-2014 NDACC/IRWG
#    This file is part of sfit4.
#
#    sfit4 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    sfit4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with sfit4.  If not, see <http://www.gnu.org/licenses/>
#
#----------------------------------------------------------------------------------------

import os
import stat
import signal
import psutil
import subprocess 
from   time       import sleep

opus_path = r"C:\Program Files (x86)\Bruker\OPUS_8.1.29\opus.exe"
opus_args = r"/OPUSPIPE=ON" r"/DIRECTLOGINPASSWORD=Admin@OPUS"

def get_pid(pName):

    pids = []

    for proc in psutil.process_iter():
        try:
            if pName in proc.name(): pids.append(proc.pid)
        except:
            pass

    return pids

def ckOPUS(overRideRestart=False):

    restartFlg = False

    #----------------------------------
    # Get PIDs of OPUS versions running
    #----------------------------------
    pids = get_pid("opus.exe")

    print ("Number of PIDs = {}".format(len(pids)))

    #---------------------------------------------
    # OverRideRestart just kills all OPUS programs 
    # and restarts no matter what the state is
    #---------------------------------------------
    if overRideRestart:
        for pid in pids:
            os.system("taskkill /F /T /PID {}".format(pid))
        #--------------------------FL0------------------------------------			
        psutil.Popen([opus_path, opus_args])

       
        sleep(20)         

    #------------------
    # Non-overRide mode
    #------------------
    else:

        #--------------------------------------------------------
        # If mulitple PIDs exist... Kill all and set restart flag
        #--------------------------------------------------------
        if len(pids) > 1:
            print ("More than one OPUS programs running. Total number = {}\n".format(len(pids)))
            print ("Killing current running OPUS programs\n")
            for pid in pids:
                os.system("taskkill /F /T /PID {}".format(pid))
            restartFlg = True
    
    
        #---------------------------------------------
        # If no OPUS programs running set restart flag
        #---------------------------------------------
        elif len(pids) == 0: 
            print ("No instances of OPUS found running. Starting new OPUS..\n")
            restartFlg = True
    
        #--------------------------------------------
        # Restart OPUS with pipes if restart flag set
        #--------------------------------------------
        if restartFlg:
		    #--------------------------FL0------------------------------------
            psutil.Popen([opus_path, opus_args])
            
            sleep(20)    

if __name__ == "__main__":
    ckOPUS()


