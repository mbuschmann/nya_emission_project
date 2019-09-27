from sr80 import sr80
import time, os
import numpy as np

if __name__ == '__main__':

    logfile = open(os.path.join('timing_sr80', 'logfile.txt'), 'w')
    sr80 = sr80()
    time.sleep(15)
    for tt in np.array([20.0, 100.0, 20.0]):
        sr80.set_temperature(tt)
        start = time.time()
        logfile.write('SR80 set to %e\n'%tt)
        t = sr80.get_stability()
        while np.abs(t[0] - tt) > 0.01 or t[1] > 0.01:
            time.sleep(2)
            t = sr80.get_stability()
            logfile.write('%e, %e, %e\n'%(time.time()-start, t[0], t[1]))
    logfile.close()
    del sr80
