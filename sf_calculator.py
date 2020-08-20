import numpy
import pandas
import matplotlib.pyplot as plt
import re

class gxCalc:

	# Default Units
	# area_disk: pc**2
	# mass_gas: M_sol
	# suface density of gas: M_sol pc**-2
	# surface density of star-formation rate: M_sol yr**-1 kpc**-2
	# total star-formation rate: M_sol yr **-1

	def __init__(self, area_disk, mass_gas):
		self.area_disk = area_disk
		self.area_disk_kpc = area_disk / 10**6 
		self.mass_gas = mass_gas 
		self.sigma_gas = (mass_gas / area_disk) 
		self.sigma_sfr = (2.5) * (10**-4) * (self.sigma_gas**1.4) # S-K relation 
		self.sfr_total = self.sigma_sfr * self.area_disk_kpc 

	def computeSigmaGas(self, area_disk, mass_gas):
	# area units: pc**2
	# mass units: M_sol
		self.sigma_gas = (mass_gas / area_disk)
		
	def computeSigmaSFR(self, sigma_gas):
	# use the Schmidt-Kennicutt relation to calculate sfr density
	# sigma_gas units: M_sol pc**-2
		self.sigma_sfr = (2.5) * (10**-4) * (sigma_gas**1.4)
		
	def computeTotalSFR(self, sigma_sfr, area_disk):
	# sigma_sfr units: M_sol yr**-1 kpc**-2
	# area units: kpc**2
		self.sfr_total = sigma_sfr * area_disk
		

def main():
# main iteratively calculates the total star-formation rate and total gas consumed, then appends sfr data to table for plotting.

	area_disk = 7.05858347*10**8 
	mass_gas = 4.45997*10**9
	interval = 0.5 # units: Gyr
	galaxy = gxCalc(area_disk, mass_gas)
	plotdata = pandas.DataFrame(
		{"time" : 0.0, "sfr_total" : [galaxy.sfr_total]}
	)
	t_elapsed = 0 + interval # units: Gyr
	while t_elapsed <= 10:
		gas_consumed = galaxy.sfr_total * interval * 10**9
		galaxy.mass_gas = galaxy.mass_gas - gas_consumed
		galaxy.computeSigmaGas(galaxy.area_disk, galaxy.mass_gas)
		galaxy.computeSigmaSFR(galaxy.sigma_gas)
		galaxy.computeTotalSFR(galaxy.sigma_sfr, galaxy.area_disk_kpc)
		row = pandas.DataFrame(
			{"time" : [t_elapsed], "sfr_total" : [galaxy.sfr_total]}
		)
		plotdata = plotdata.append(row)
		t_elapsed += interval

	# TODO error bars for total_sfr values
	fig, axs = plt.subplots(
		figsize=(6,6),
		dpi=120,
	)
	axs.plot(
		plotdata['time'],
		plotdata['sfr_total'],
		ls='',
		marker='s'
	)
	axs.grid(
		b=True,
		which='major',
		axis='y',
	)
	plt.xticks(numpy.arange(0,11,1))
	plt.xlabel(
		'$t-t_0$ ' + '[Gyr]',
		size=15
	) 
	plt.ylabel(
		'Total star-formation ' + '[$M_{\odot} yr^{-1}$]',
		size=15
	)	 
	plt.tight_layout()
	plt.show()

main()
