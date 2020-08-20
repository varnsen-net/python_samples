import numpy as numpy
import pandas as pandas
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import seaborn as sea



residcat = (pandas.read_csv(
	'/home/w3rkman/astro/catalogs/v3_ResidClass/internal_residcat_wparams.csv',
	index_col='ID'
	)
	.sort_index()
)


# Fixes incorrect data type for log_sSFR column and excludes -inf values
residcat.log_sSFR = residcat.log_sSFR.astype(float)
residcat = residcat.query('log_sSFR > -999 \
	and M_med > 0 \
	and r50_kpc > 0 \
	and q_apert > 0 \
	and sig1 > 0'
)

### RESIDFLAGS AND REDSHIFT BINS ###
def makeMasses(row):

	row.M_med = float(row.M_med)

	if row.M_med > 0 and row.M_med <= 10:
		return '9.7 < M_med < 10'
		
	elif row.M_med > 10	and row.M_med <= 10.5:
		return '10 < M_med < 10.5'
		
	elif row.M_med > 10.5:
		return 'M_med > 10.5'
		
	else:
		return numpy.nan

residcat['massbin'] = residcat.apply(makeMasses, axis=1)
print(residcat.massbin.value_counts())

zbin = {
	1: residcat.query('1.0 <= zbest < 1.4'),
	2: residcat.query('1.4 <= zbest < 1.8'),
	3: residcat.query('1.8 <= zbest < 2.2'),
	4: residcat.query('2.2 <= zbest <= 2.5'),
}




### PLOT ###
fig, axs = plt.subplots(
	2,2,
	figsize=(10,10),
	sharex=True,
	sharey=True,
	dpi=120,
)


for panel, ax in enumerate(axs.ravel(),1):
	sea.kdeplot(
		zbin[panel].query('log_sSFR > -9.5')['sig1'], 
		zbin[panel].query('log_sSFR > -9.5')['log_sSFR'] + 9,
		bw='scott',
		shade=True,
		shade_lowest=False,
		color='xkcd:blue',
		alpha=0.4,
		zorder=0,
		ax=ax,
	)
	sea.kdeplot(
		zbin[panel].query('log_sSFR < -9.5')['sig1'], 
		zbin[panel].query('log_sSFR < -9.5')['log_sSFR'] + 9,
		bw='scott',
		shade=True,
		shade_lowest=False,
		color='xkcd:red',
		alpha=0.4,
		zorder=0,
		ax=ax,
	)
	massbin = zbin[panel]['massbin']
	sizes = {
		'9.7 < M_med < 10' : 20,
		'10 < M_med < 10.5' : 40,
		'M_med > 10.5' : 60
	}
	sea.scatterplot(
		zbin[panel].query('ResidFlag == "asym_pec"')['sig1'], 
		zbin[panel].query('ResidFlag == "asym_pec"')['log_sSFR'] + 9,
		size=massbin,
		sizes=sizes,
		facecolor='xkcd:mango',
		edgecolor='xkcd:almost black',
		marker='s',
		linewidth=0.5,
		alpha=1,
		zorder=3,
		ax=ax
	)
	sea.scatterplot(
		zbin[panel].query('ResidFlag == "XH"')['sig1'], 
		zbin[panel].query('ResidFlag == "XH"')['log_sSFR'] + 9,
		size=massbin,
		sizes=sizes,
		facecolor='xkcd:seafoam',
		edgecolor='xkcd:almost black',
		marker='d',
		linewidth=0.5,
		alpha=1,
		zorder=4,
		ax=ax
	)
	
	### Create custom legend to get rid of the stupid one seaborn makes
	residflag_elements = [
		Line2D([0],[0],
		label='Compact',
		markerfacecolor='xkcd:seafoam',
		marker='d',
		ms=8,mec='black',mew=0.5,ls='None'),
		
		Line2D([0],[0],
		label='Peculiar',
		markerfacecolor='xkcd:mango',
		marker='s',
		ms=8,mec='black',mew=0.5,ls='None'),
	]
	massbin_elements = [
		Line2D([0],[0],
		label='$9.7 < \log M_{*} < 10.0$',
		color='xkcd:black',
		marker='o',
		ms=4,mec='black',mew=0.5,ls='None'),
		
		Line2D([0],[0],
		label='$10.0 < \log M_{*} < 10.5$',
		color='xkcd:black',
		marker='o',
		ms=6,mec='black',mew=0.5,ls='None'),
		
		Line2D([0],[0],
		label='$\log M_{*} > 10.5$',
		color='xkcd:black',
		marker='o',
		ms=8,mec='black',mew=0.5,ls='None')
	]
	ax.plot(
		[9.6,9.6],
		[2,-3],
		linestyle='-',
		linewidth=1,
		color='xkcd:black',
		zorder=5,
	)
	ax.plot(
		[6,11.5],
		[-0.5,-0.5],
		linestyle='-',
		linewidth=1,
		color='xkcd:black',
		zorder=5,
	)

	ax.tick_params(labelsize=15)
	ax.set(
		xlabel='',
		ylabel='',
		xlim=(7,11),
		ylim=(2,-3),
		xticks=[7.5, 8.5, 9.5, 10.5],
		yticks=[1.5,1,0.5,0,-0.5,-1,-1.5,-2,-2.5],
	)
	ax.get_legend().remove()

axs[0,0].legend(
	handles=residflag_elements, 
	loc=2, 
	fontsize='small', 
	title='Morphology', 
	framealpha=1.0
)
axs[1,1].legend(
	handles=massbin_elements, 
	loc=2, 
	fontsize='small', 
	title='Mass Bins', 
	framealpha=1.0
)

axs[0,0].text(
	9.7,1.9,
	'$1.0 < z < 1.4$',
	size=14
)
axs[0,1].text(
	9.7,1.9,
	'$1.4 < z < 1.8$',
	size=14
)
axs[1,0].text(
	9.7,1.9,
	'$1.8 < z < 2.2$',
	size=14
)
axs[1,1].text(
	9.7,1.9,
	'$2.2 < z < 2.5$',
	size=14
)

plt.figtext(
	0.55,0.04,
	'$\log{\ \Sigma_{1 \mathrm{kpc}}}\ \mathrm{[M_{\odot}\ kpc^{-2}]}$',
	ha='center',
	va='center',
	fontsize=28)
plt.figtext(
	0.04,0.55,
	'$\log{\ sSFR}\ \mathrm{[Gyr^{-1}]}$',
	ha='center',
	va='center',
	rotation='vertical',
	fontsize=28)


plt.tight_layout(rect=[0.075, 0.075, 1, 1])


plt.show()












