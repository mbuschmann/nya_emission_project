import sys
sys.path.append('../ftsreader')

from fft_ftir import fft_ftir
from ftsreader import ftsreader
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import h,c,k



def planck(freq,ts):
    return(2e8*h*c**2*freq**3/(np.exp(100*h*c*freq/(k*(ts+273.15)))-1))

fft = fft_ftir()

cold = fft.fft('..\\output\\test5\\nyem20190822112406_bb_20.00.000')
hot = fft.fft('..\\output\\test5\\nyem20190822114034_bb_100.00.000')
atmo = fft.fft('..\\output\\test5\\nyem20190822112741_up.000')

hotcold = (hot['spectrum_fwd'] - cold['spectrum_fwd'])
atmcold = (atmo['spectrum_fwd'] - cold['spectrum_fwd'])

wvn = hot['wvn_fwd']
#complex spectra
calib = planck(wvn,100.0) - planck(wvn,20.0)
calib = np.real(calib / hotcold * atmcold + planck(wvn,20.0))

# interferogram
npt_long = len(hot['ifg_fwd'])
wvn_i = np.fft.fftfreq(int(npt_long), 0.5 / fft.laser_wvn)[:int(npt_long / 2)]
hotcold_i = np.fft.ifft(hot['ifg_fwd'] - cold['ifg_fwd'])[:int(npt_long/2)]
atmcold_i = np.fft.ifft(atmo['ifg_fwd'] - hot['ifg_fwd'])[:int(npt_long/2)]

calib_i = planck(wvn_i,100.0) - planck(wvn_i,20.0)
calib_i = calib_i / hotcold_i * (atmcold_i) + planck(wvn_i,100.0)

f = plt.figure()
f.clf()
plt.plot(wvn,calib)
plt.plot(wvn_i,np.real(calib_i))
f.show()

input()
