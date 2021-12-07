#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 10:00:35 2021

@author: katherinedelgado
"""

import csv
import numpy
import ResponseClass 
from pylab import *

def read_csv_file(filename, header=True):
	data = []
	with open(filename, newline='') as csvfile:
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			data.append(row)
	if header==True:
		out_header = data[0]
		out = data[1:]
		return out, out_header
	else:
		return out

def write_csv(filename,data,header):
	with open(filename, "w") as f:
		writer= csv.writer(f)
		writer.writerow(header)
		for row in data:
			writer.writerow(row)

def count_frames(filename,threshold=1):
	"""Reads in a stimulus output file and assigns an image frame number to each stimulus frame."""
	rows,header = read_csv_file(filename) #import stim file
	R = numpy.asarray(rows,dtype='float') # convert stim file list to an array
	#set up the output array
	output_array=numpy.zeros((R.shape[0],R.shape[1]+1))
	header.extend(['frames']) 
	#calculate change in voltage signal
	vs = [0]
	vs.extend(R[1:,-1]-R[:-1,-1])
	#count image frames based on the change in voltage signal
	count_on = 0
	F_on = [0]
	count_off = 0
	F_off = [0]
	frame_labels = [0]
	n = 1
	while n<len(vs)-1:
		if vs[n]>vs[n-1] and vs[n]>vs[n+1] and vs[n] > threshold:
			count_on = count_on+1
			F_on.extend([count_on])
			F_off.extend([count_off])
		elif vs[n]<vs[n-1] and vs[n]<vs[n+1] and vs[n] < threshold*-1:
			count_off = count_off - 1
			F_off.extend([count_off])
			F_on.extend([F_on])
		else:
			F_on.extend([count_on])
			F_off.extend([count_off])
		frame_labels.extend([count_on*(count_on+count_off)])
		n=n+1
	frame_labels.extend([0])
	output_array[:,:R.shape[1]] = R
	output_array[:,-1] = frame_labels
	OAS = output_array[output_array[:,-1].argsort()]
	i1 = numpy.searchsorted(OAS[:,-1],1)
	OASc = OAS[i1:,:] #removes rows before image series start
	output_list = []
	n = 0
	frame=1
	same_frame = []
	while n<len(OASc):
		if int(OASc[n,-1])==frame:
			same_frame.append(list(OASc[n,:]))
		else:
			output_list.append(same_frame[0])
			same_frame = []
			same_frame.append(list(OASc[n,:]))
			frame=frame+1
		n=n+1
	output_list.append(same_frame[0])
	return output_list,header

def parse_stim_file(stim_info_array,indices = {'frames':-1, 'global_time':1, 'rel_time':2, 'stim_state':False, 'stim_type':False}):
	"""Get frame numbers, global time, relative time per epoch, and stim_state (if it's in the stim_file"""
	frames = stim_info_array[:,indices['frames']]
	global_time = stim_info_array[:,indices['global_time']]
	rel_time = stim_info_array[:,indices['rel_time']]
	return frames, global_time, rel_time

def define_stim_state(rel_time,on_time,off_time):
	stim_state = []
	for t in rel_time:
		if t>on_time and t<off_time:
			stim_state.extend([1])
		else:
			stim_state.extend([0])
	return stim_state


