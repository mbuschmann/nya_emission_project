import sys
sys.path.append('../../ftsreader/')
from ftsreader import ftsreader
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from scipy.constants import h,c,k
import numpy as np
import matplotlib.pyplot as plt

class fft_ftir():
    def __init__(self):
        self.laser_wvn = 15798.208689 # HeNe wavelength in vacuum

    def _ifg_to_spc(self,ifg,cb):
        npt = len(ifg)
        npt_long = 0
        nr = 1
        while npt_long < npt:
            npt_long = 2**nr
            nr +=1

        mean = np.mean(ifg[cb+512:])

        ifg_long = np.zeros(npt_long)
        ifg_long[:npt-cb] = ifg[cb:npt] - mean
        ifg_long[-cb:] = ifg[:cb] - mean

        wvn =  np.fft.fftfreq(int(npt_long),0.5/self.laser_wvn)[:int(npt_long/2)]
        spectrum = np.array(np.fft.ifft(ifg_long))[:int(npt_long/2)]

        return(wvn, ifg_long, spectrum)

    def fft(self, fts_file):
        meas  = ftsreader(fts_file, getifg=True,getspc=True)
        spectrum = {};
        aqm = meas.header['Acquisition Parameters']['AQM']
        bwd = False
        # if interferograms in both directions? (forward-backward?)
        if aqm =='SD':
            bwd = True
        cb1 = meas.header['Instrument Parameters']['PKL']
        if bwd:
            # CB2 is already in the frame of the length of a single IFG
            cb2 = meas.header['Instrument Parameters']['PRL']
            npt = int(meas.header['Data Parameters IgSm']['NPT']/2)
        else:
            npt = int(meas.header['Data Parameters IgSm']['NPT'])

# Split interferogram
        ifg_fwd = meas.ifg[:int(npt)]

        spectrum['ifg'] = meas.ifg
        spectrum['wvn_fwd'], spectrum['ifg_fwd'], spectrum['spectrum_fwd'] = self._ifg_to_spc(ifg_fwd, cb1)
        if bwd:
            ifg_bwd = meas.ifg[int(npt)+1:][::-1]
            spectrum['wvn_bwd'], spectrum['ifg_bwd'], spectrum['spectrum_bwd'] = self._ifg_to_spc(ifg_bwd, npt-cb2)

        #average spectrum

        spectrum['wvn'] = spectrum['wvn_fwd']
        spectrum['spectrum'] = spectrum['spectrum_fwd']
        if bwd:
            spectrum['spectrum'] = spectrum['spectrum'] + np.interp(spectrum['wvn_fwd'], spectrum['wvn_bwd'], spectrum['spectrum_bwd'])
            spectrum['spectrum'] = spectrum['spectrum'] / 2.0
   #         spectrum['spectrum'] = np.mean((spectrum['spectrum_fwd'],np.interp(spectrum['wvn_fwd'], spectrum['wvn_bwd'], spectrum['spectrum_bwd'])))
        return(spectrum)



if __name__ == '__main__':

    s = fft_ftir()
    fts_file = input()
    meas  = ftsreader(fts_file, getifg=True, getspc=True)
#    spectrum = s.fft('/home/mathias/projects/Vertex80_Emi/Totalpower_Atmosphere/BBSR80_100.0')
    spectrum = s.fft(fts_file)
    f = plt.figure()
    plt.plot(spectrum['wvn_fwd'], np.abs(spectrum['spectrum_fwd']),'b')
    plt.plot(spectrum['wvn_bwd'], np.abs(spectrum['spectrum_bwd']),'g')
    plt.plot(spectrum['wvn'], np.abs(spectrum['spectrum']),'k')
    f.show()

    input()
