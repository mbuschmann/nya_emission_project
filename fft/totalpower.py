import sys
sys.path.append('../ftsreader')

from ftsreader import *
import matplotlib.pyplot as plt
from scipy.constants import h,c,k

def planck(freq,ts):
    return(2e8*h*c**2*freq**3/(np.exp(100*h*c*freq/(k*(ts+273.15)))-1))

cold = ftsreader('..\\output\\test5\\nyem20190822112406_bb_20.00.000',getifg=True)
hot = ftsreader('..\\output\\test5\\nyem20190822114034_bb_100.00.000',getifg=True)
atmo = ftsreader('..\\output\\test5\\nyem20190822112741_up.000',getifg=True)

calib = ftsreader('..\\output\\test5\\CalibSpectrum.0',getspc=True)


npt_c = int(cold.header['Data Parameters IgSm']['NPT'])
cb1_c = int(cold.header['Instrument Parameters']['PKL'])
cb2_c = int(npt_c - cold.header['Instrument Parameters']['PKL'])

ifg_c = np.zeros(2**19)
mean_c = np.mean(cold.ifg[cb1_c:int(npt_c/2)])
ifg_c[0:int(npt_c/2)-cb1_c] = cold.ifg[cb1_c:int(npt_c/2)] - mean_c
ifg_c[-cb1_c:] = cold.ifg[:cb1_c] - mean_c
spectrum_c = np.fft.ifft(ifg_c)[:int(2**19/2)]

npt_h = hot.header['Data Parameters IgSm']['NPT']
cb1_h = hot.header['Instrument Parameters']['PKL']
cb2_h = npt_h - hot.header['Instrument Parameters']['PKL']

ifg_h = np.zeros(2**19)
mean_h = np.mean(hot.ifg[cb1_h:int(npt_h/2)])
ifg_h[0:int(npt_h/2)-cb1_h] = hot.ifg[cb1_h:int(npt_h/2)] - mean_h
ifg_h[-cb1_h:] = hot.ifg[:cb1_h] - mean_h

spectrum_h = np.fft.ifft(ifg_h)[:int(2**19/2)]

npt_a = atmo.header['Data Parameters IgSm']['NPT']
cb1_a = atmo.header['Instrument Parameters']['PKL']
cb2_a = npt_a - atmo.header['Instrument Parameters']['PKL']
sr_a = 1.0e-3/float(hot.header['Optic Parameters']['VEL'])

ifg_a = np.zeros(2**19)
mean_a = np.mean(atmo.ifg[cb1_a:int(npt_a/2)])
ifg_a[0:int(npt_a/2)-cb1_a] = atmo.ifg[cb1_a:int(npt_a/2)] - mean_a
ifg_a[-cb1_a:] = atmo.ifg[:cb1_a] - mean_a

spectrum_a = np.fft.ifft(ifg_a)[:int(2**19/2)]
freq_a =  np.fft.fftfreq(int((2**19)/2),1.0/15798.21)

spectrum_h = spectrum_h[6000:int(spectrum_h.size/2)]
spectrum_c = spectrum_c[6000:int(spectrum_c.size/2)]
spectrum_a = spectrum_a[6000:int(spectrum_a.size/2)]

freq_h = freq_a[6000:int(freq_a.size/2)]
freq_c = freq_a[6000:int(freq_a.size/2)]
freq_a = freq_a[6000:int(freq_a.size/2)]


f = plt.figure('Spectra')
f.clf()
plt.plot(freq_a[:int(freq_a.size/2)], np.abs(spectrum_h[:int(spectrum_a.size/2)]))
plt.plot(freq_a[:int(freq_a.size/2)], np.abs(spectrum_c[:int(spectrum_a.size/2)]))
plt.plot(freq_a[:int(freq_a.size/2)], np.abs(spectrum_a[:int(spectrum_a.size/2)]))
f.show()

tpow = (planck(freq_a,100.0) - planck(freq_a,20.0))
tpow = tpow / (spectrum_h - spectrum_c)
tpow = tpow * (spectrum_a - spectrum_c)

f = plt.figure('Total Power')

#plt.plot(freq_a, np.imag(tpow))

tpow = (planck(freq_a,100.0) - planck(freq_a,20.0))
tpow = tpow / (np.abs(spectrum_h - spectrum_c))
tpow = tpow * (np.abs(spectrum_a - spectrum_c))
tpow = tpow + planck(freq_a ,20.0)
plt.plot(freq_a, tpow, label='Magnitude Spectra')

tpow = (planck(freq_a,100.0) - planck(freq_a,20.0))
tpow = tpow / (np.real(spectrum_h - spectrum_c))
tpow = tpow * (np.real(spectrum_a - spectrum_c))
tpow = tpow + planck(freq_a ,20.0)
plt.plot(freq_a, tpow, label='Real part')

plt.plot(freq_a, np.real(tpow1), label='Complex Spectra')

plt.plot(calib.spcwvn, calib.spc, label='OPUS calib with igrams')
plt.legend()
f.show()

input()
