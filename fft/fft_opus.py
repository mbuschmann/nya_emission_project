import sys
sys.path.append('../ftsreader')
from ftsreader import ftsreader
import matplotlib.pyplot as plt

op1 = ftsreader('./20190618/BBIR563_100.0')

npt = op1.header['Data Parameters IgSm']['NPT']
cb1 = op1.header['Instrument Parameters']['PKL']
cb2 = npt - op1.header['Instrument Parameters']['PKL']
phase_ifg_1 = np.zeros(2**17)
phase_ifg_1[0:512] = op1.ifg[cb1:cb1+512]
phase_ifg_1[-511:] = op1.ifg[cb1-511:cb1]


phase_spec_1 = np.fft.ifft(phase_ifg_1-np.mean(phase_ifg_1))

power_1 = np.abs(phase_spec_1[0:2**17/2])
phase_spec_1_real = np.real(phase_spec_1[0:2**17/2]) * power_1
phase_spec_1_imag = np.imag(phase_spec_1[0:2**17/2]) * power_1

f1 = plt.figure('Phase spectra')
f1.clf()

plt.plot(phase_spec_1_real)
plt.plot(phase_spec_1_imag)

f1.show()

f2 = plt.figure('Phase interferogram')
f2.clf()

plt.plot(phase_ifg_1)

f2.show()



ifg_1 = np.zeros(2**17)
ifg_1[0:npt/2-cb1] = op1.ifg[cb1:npt/2]
ifg_1[-cb1:] = op1.ifg[:cb1]
ifg_1 = ifg_1-np.mean(ifg_1)

spc_1 = np.fft.ifft(ifg_1-np.mean(ifg_1))

f = plt.figure('Interferogram')
plt.plot(ifg_1)
f.show()

f = plt.figure('Spectrum')
f.clf()
nn = 2**17/2
spc = spc_1[0:nn] * (phase_spec_1_real + phase_spec_1_imag*1j)
plt.plot(np.real(spc)/np.max(np.real(spc)))
plt.plot(np.flipud(np.array(op1.spc))/np.max(op1.spc))
f.show()
