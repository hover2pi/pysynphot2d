#!/usr/bin/python
# -*- coding: latin-1 -*-
"""
Description
-----------
`pysynphot` has the `ArraySpectrum` and `Observation` classes to handle 1D spectra. 
This class accepts 2D flux arrays (thus the names `ArraySpectra` and `Observations`)
and vectorizes all `ArraySpectrum` and `Observation` attribute calls.

Authors
-------
Joe Filippazzo, 2017-12-21
"""
import numpy as np
import pysynphot as ps
import matplotlib.pyplot as plt

class ArraySpectra(object):
    """
    This is a wrapper class for pysynphot.ArraySpectrum() so it can handle ND spectra
    """
    def __init__(self, wave, flux, **kwargs):
        """
        Initialize the object
        
        Parameters
        ----------
        wave: sequence
            The wavelength array
        flux:
            The flux cube
        
        Example
        -------
        import os
        import ExoCTK
        import pysynphot2d
        grid = ExoCTK.core.ModelGrid(os.environ['MODELGRID_DIR'], resolution=100, Teff_rng=(3400,3500), logg_rng=(4.5,5.5), FeH_rng=(0,0), wave_rng=(0.8,2.5))
        model = grid.get(3500, 5, 0)
        model['wave'] *= 10000
        spec2D = pysynphot2d.psp2d.ArraySpectra(**model)
        """
        # Create object for each 1D spectrum
        self.spectra = [ps.ArraySpectrum(wave, f, name=n) for n,f in enumerate(flux)]
        
        # Store other inputs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __getattribute__(self, attr):
        """
        Redefining the getattribute call to iterate over the list of 1D spectra
        
        Parameters
        ----------
        attr: str
            The attribute to call
        
        Returns
        -------
        np.ndarray
            An array of the results
        """
        # Try to get the attribute from the parent object
        try:
            return super().__getattribute__(attr)
            
        # If that fails, check the child object
        except AttributeError:
            
            # If it is a method...
            if callable(getattr(self.spectra[0], attr)):
                results = lambda *args, **kwargs: self._vec_attr(attr, *args, **kwargs)
                
            # ... or just an attribute
            else:
                results = np.array([getattr(data1D, attr) for data1D in self.spectra])
            
        return results
                
    def _vec_attr(self, attr, *args, **kwargs):
        """
        Iterate over the 1D spectra
        
        Parameters
        ----------
        attr: str
            The attribute to call
        
        Returns
        -------
        np.ndarray
            The vectorized results
        """
        return np.array([getattr(data1D, attr)(*args, **kwargs) for data1D in self.spectra])
        
    def plot(self, idx, param=''):
        """
        Plot the spectrum
        
        Parameters
        ----------
        idx: int
            The index of the spectrum to plot
        param: str
            The name of the parameter to print
        """
        obs = self.spectra[idx]
        if param:
            p = getattr(self, param)
            plt.plot(obs.wave, obs.flux, label='{} @ {} = {}'.format(obs.name,param,p[idx]))
        else:
            plt.plot(obs.wave, obs.flux, label=obs.name)
            
        plt.xlabel(obs.waveunits)
        plt.ylabel(obs.fluxunits)
        plt.legend(loc=0)
        
class Observations(object):
    """
    This is a wrapper class for pysynphot.Observtion() so it can handle ND spectra
    """
    def __init__(self, spec2D, band, **kwargs):
        """
        Initialize the object
        
        Parameters
        ----------
        spec2D: ArraySpectra
            The 2D spectra
        band: ps.spectrum.SpectralElement
            The bandpass
        
        Example
        -------
        import os
        import ExoCTK
        import pysynphot
        import pysynphot2d
        grid = ExoCTK.core.ModelGrid(os.environ['MODELGRID_DIR'], resolution=100, Teff_rng=(3400,3500), logg_rng=(4.5,5.5), FeH_rng=(0,0),wave_rng=(0.8,2.5))
        model = grid.get(3500, 5, 0)
        model['wave'] *= 10000
        spec2D = pysynphot2d.psp2d.ArraySpectra(**model)
        bp = pysynphot.ObsBandpass('wfc3,ir,g141')
        obs = pysynphot2d.psp2d.Observations(spec2D, bp)
        """
        # Create object for each 1D spectrum
        self.spectra = [ps.Observation(spec, band) for spec in spec2D.spectra]
        
        # Store other inputs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __getattribute__(self, attr):
        """
        Redefining the getattribute call to iterate over the list of 1D spectra
        
        Parameters
        ----------
        attr: str
            The attribute to call
        
        Returns
        -------
        np.ndarray
            An array of the results
        """
        # Try to get the attribute from the parent object
        try:
            return super().__getattribute__(attr)
            
        # If that fails, check the child object
        except AttributeError:
            
            # If it is a method...
            if callable(getattr(self.spectra[0], attr)):
                results = lambda *args, **kwargs: self._vec_attr(attr, *args, **kwargs)
                
            # ... or just an attribute
            else:
                results = np.array([getattr(data1D, attr) for data1D in self.spectra])
            
        return results
                
    def _vec_attr(self, attr, *args, **kwargs):
        """
        Iterate over the 1D spectra
        
        Parameters
        ----------
        attr: str
            The attribute to call
        
        Returns
        -------
        np.ndarray
            The vectorized results
        """
        return np.array([getattr(data1D, attr)(*args, **kwargs) for data1D in self.spectra])
        
    def plot(self, idx):
        """
        Plot the observation
        
        Parameters
        ----------
        idx: int
            The index of the spectrum to plot
        """
        obs = self.spectra[idx]
        plt.plot(obs.wave, obs.flux, label='native, {}'.format(obs.name))
        plt.step(obs.binwave, obs.binflux, label='binned, {}'.format(obs.name))
        plt.xlabel(obs.waveunits)
        plt.ylabel(obs.fluxunits)
        plt.legend(loc=0)