# -*- coding: UTF-8 -*-

from matplotlib.figure import Figure
from matplotlib.patches import Circle
import dropbox
import shutil
import errno
import csv
import os
import glob
from optparse import OptionParser
import numpy as np
from astropy.io import fits,ascii
from astropy.visualization import (MinMaxInterval,PercentileInterval,ZScaleInterval,SqrtStretch,AsinhStretch,LogStretch,ImageNormalize)
import matplotlib.pyplot as plt

def validAccessToken(dbox):
	# returns true if the access token links to a valid account, else returns
	# false. if the token is bad, this function will print a less oblique error
	# message than the one given by python.
	try:
		usracct = dbox.users_get_current_account()
		print("Connected to account: " + usracct.name.display_name + "\n")
		return True
	except dropbox.exceptions.AuthError:
		print("Your Dropbox access token is invalid. Please check the access token given in this script against the access token for this app on Dropbox.\n")
		return False

def createLocalFolder(csvfilename, foldername, local_dir):
	# creates a folder in the cwd corresponding to a given filename. if the
	# folder already exists, we will delete it and create a new folder.
	# print("Creating directory: " + local_dir)
	try:
		os.mkdir(local_dir)
	except OSError as e:
		if e.errno == errno.EEXIST:
			shutil.rmtree(local_dir)
			os.mkdir(local_dir)
		else:
			raise

def downloadFITS(dbox,dropbox_fits_dir, csvfilename, local_dir):
	# creates an iterable object from a given csv file and downloads each FITS
	# file listed in the csv. the csv must have a single column with a header.
	# the header can be any string.
	#     gxlist = ascii.read(os.getcwd()+'/'+csvfilename+'.csv',format='csv')
	#     next(np.array(gxlist['ID']))

	with open(os.getcwd()+'/'+csvfilename+'.csv') as file:
		gxlist = csv.reader(file)
		next(gxlist)
		for each_gal in gxlist:
			filename = each_gal[0]
			# print filename
			# print dropbox_fits_dir + filename
			# print local_dir + filename
			dbox.files_download_to_file(local_dir + filename, dropbox_fits_dir + filename)
			print("Saving: " + filename)
	return

def download_files_from_dropbox(token,dropbox_dir,working_dir,csvfilename):
	dbox = dropbox.Dropbox(token)
	if validAccessToken(dbox):
		foldername = csvfilename.split(".csv")[0]
		local_dir = working_dir + "/" + foldername + "/"
		createLocalFolder(csvfilename, foldername, local_dir)
		downloadFITS(dbox,dropbox_dir, csvfilename, local_dir)
	return

def cropFITS(fits_array):
	# center-crops an m×n array into an m×m or n×n array (whichever is smaller, m or n).
	y,x = fits_array.shape
	crop_size = min((y,x))
	startx = x//2 - crop_size//2
	starty = y//2 - crop_size//2
	return fits_array[starty:starty+crop_size, startx:startx+crop_size]

def fixR50coordinate(fits_array, xR50, yR50):
	# adjusts the R50 location for a center-cropped array.
	y,x = fits_array.shape
	if x > y: # i.e., if array has more cols than rows.
		xshift = (x-y)//2
		xR50 = xR50 - xshift
	elif y > x: # i.e., if array has more rows than cols.
		yshift = (y-x)//2
		yR50 = yR50 - yshift
	return xR50, yR50

def getArraysFromCube(filename):
	# get every image array from a fits image cube.
	with fits.open(filename) as cube:
		original = cube[1].data
		model = cube[2].data
		residual = cube[3].data
		model_header = cube[2].header
		return original, model, residual, model_header

def createR50patch(cube_data):
	model_header = cube_data[3]
	radius = float(model_header['2_RE'].split()[0].strip('*'))
	xobj, yobj = (float(model_header['2_XC'].split()[0]) - 1, float(model_header['2_YC'].split()[0]) - 1)
	xobj, yobj = fixR50coordinate(cube_data[0], xobj, yobj)
	circle = Circle((xobj, yobj), radius, color='cyan', fill=False, alpha=0.7)
	return circle

def plotFITS(cube_data, user_selections, destination, filename):
	# plot the user-selected arrays from a FITS image cube. 
	# each user-seelcted array is mapped to a figure ax.
	# the figure properties are automagically determined from the user selections.
	user_selections = [f-1 for f in user_selections] # because numpy uses 0-indexing
	ncols = len(user_selections)
	normalization = ImageNormalize(
		cube_data[0], 
		interval=PercentileInterval(99.5),
		stretch=AsinhStretch()
	)
	fig, axs = plt.subplots(nrows=1,ncols=ncols,figsize=[ncols*6,6])
	if len(user_selections) < 2: # if the user selected a single slice, then we need to make the axs variable an iterable for zip().
		axs = [axs]
	ax_map = zip(user_selections, axs)
	for row in ax_map:
		selection = row[0]
		ax = row[1]
		fits_array = cube_data[selection]
		fits_array = cropFITS(fits_array)
		ax.imshow(fits_array,origin='lower',cmap='gray',norm=normalization)
		ax.set_axis_off()
	circle = createR50patch(cube_data)
	axs[-1].add_patch(circle) # we'll only add the R50 to the last ax in our list of axs.
	plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0.01)
	png_name = os.path.basename(filename).strip('.fits')+'.png'
	plt.savefig(destination+'/'+png_name,format='png')
	plt.close()
	return

def main():
	parser = OptionParser()
	parser.add_option("--c", "--catalog",
					  action="store", type="string", dest="catalog_name")

	parser.add_option("--f", "--format",
					  action="store", type="int", dest="format")
	options, args = parser.parse_args()

	catalog = ascii.read(options.catalog_name,format='csv')
	cwd = os.getcwd()
	mydb_token = ''
	im_path_in_my_db = "/bharath/Tidal_Residual_Classifications/CAN_Residual_Classification_images/"

	print options.catalog_name
	if not os.path.exists(os.path.basename(options.catalog_name).split(".csv")[0]):
		download_files_from_dropbox(mydb_token,im_path_in_my_db,cwd,os.path.basename(options.catalog_name).split(".csv")[0])
		img_dir = os.getcwd()+'/'+os.path.basename(options.catalog_name).split(".csv")[0]
	elif os.path.exists(os.path.basename(options.catalog_name).split(".csv")[0]):
		img_dir = os.getcwd()+'/' + os.path.basename(options.catalog_name).split(".csv")[0]
		print 'Images Exist in the Temp Folder (%s) that Matches your CSV name (%s).. using them'%(os.path.basename(options.catalog_name).split(".csv")[0],os.path.basename(options.catalog_name))
		pass

	list_of_fits_in_folder = glob.glob('%s/*.fits'%img_dir)

	png_destination_folder=os.path.basename(options.catalog_name).split(".csv")[0]+'_pngs_%sCol'%len(str(options.format))

	if not os.path.exists(os.getcwd()+'/'+png_destination_folder):
		os.mkdir(png_destination_folder)

	for filename in list_of_fits_in_folder:
		cube_data = getArraysFromCube(filename)
		user_selections = [int(f) for f in str(options.format)]
		plotFITS(cube_data, user_selections, png_destination_folder, filename)
		
main()
