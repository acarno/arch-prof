#!/usr/bin/env python



from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot



from plotly.graph_objs import Bar, Scatter, Figure, Layout



import pandas as pd

import plotly.plotly as py

import plotly.graph_objs as go

import os

import errno

import argparse

import fnmatch

import numpy as np



py.sign_in('fazla', '2u3ejlvzxx')



arm_dir = "arm_logs/"

x86_dir = "x86_logs/"



def parse_arguments():

	parser = argparse.ArgumentParser()

	parser.add_argument('bench_name', help='Name of the bench.class')

	args = parser.parse_args()

	return args



def energy(time, power):

	energy = 0

	for i in range(time.size -1 ):

		energy = energy + (time[i+1] - time[i])*(power[i] + power[i+1])/2

	return energy/1000.0



def draw(bench_name):

	data_x86 = pd.DataFrame(columns=['Thread', 'x86_core_energy', 'x86_pkg_energy','x86_time', 'x86_performance'])

	

	for filename in os.listdir(x86_dir):

		if fnmatch.fnmatch(filename, bench_name + '*'):

			#print("%s" % filename)



			token = filename.split('.')

			Benchmark = token[0]

			Class = token[1]

			Thread = token[2]

			

			data_x86.set_value(Thread, 'Thread', Thread)

			#Get x86 log file

			df = pd.read_csv(x86_dir+filename, header=None, skiprows=4)



			df[0] = df[0] - df[0][0]#Start from time 0

			

			data_x86.set_value(Thread, 'x86_core_energy', energy(df[0], df[1]))

			data_x86.set_value(Thread, 'x86_pkg_energy', energy(df[0], df[2]))

			data_x86.set_value(Thread, 'x86_time', df[0][df[0].size-1])

			data_x86.set_value(Thread, 'x86_performance', 1/df[0][df[0].size-1])

	#ARM

	data_arm = pd.DataFrame(columns=['Thread', 'arm_core_energy', 'arm_pkg_energy', 'arm_time', 'arm_performance'])



	for filename in os.listdir(arm_dir):

		if fnmatch.fnmatch(filename, bench_name + '*'):

			#print("%s" % filename)



			token = filename.split('.')

			Benchmark = token[0]

			Class = token[1]

			Thread = token[2]

			data_arm.set_value(Thread, 'Thread', Thread)

			df = pd.read_csv(arm_dir+filename, header=None, skiprows=4)

			#If corresponding ARM Log file not available

			

			df[0] = df[0] - df[0][0]#Start from time 0

			core = (df[1] + df[2])

			package = df[3] + core



			data_arm.set_value(Thread, 'arm_core_energy', energy(df[0], core))

			data_arm.set_value(Thread, 'arm_pkg_energy', energy(df[0], package))

			data_arm.set_value(Thread, 'arm_time', df[0][df[0].size-1])

			data_arm.set_value(Thread, 'arm_performance', 1/df[0][df[0].size-1])



	print(data_x86)

	print(data_arm)



	trace1 = go.Scatter(x=data_x86['Thread'], y=data_x86['x86_core_energy'], mode='lines+markers', name='x86 Core')

	trace2 = go.Scatter(x=data_x86['Thread'], y=data_x86['x86_pkg_energy'], mode='lines+markers', name='x86 Package')

	trace3 = go.Scatter(x=data_arm['Thread'], y=data_arm['arm_core_energy'], mode='lines+markers', name='ARM Core')

	trace4 = go.Scatter(x=data_arm['Thread'], y=data_arm['arm_pkg_energy'], mode='lines+markers', name='ARM Package')



	trace5 = go.Scatter(x=data_x86['Thread'], y=data_x86['x86_time'], mode='lines+markers', name='x86')

	trace6 = go.Scatter(x=data_arm['Thread'], y=data_arm['arm_time'], mode='lines+markers', name='ARM')



	trace7 = go.Scatter(x=data_x86['x86_performance'], y=data_x86['x86_pkg_energy'], mode='lines+markers', name='x86')

	trace8 = go.Scatter(x=data_arm['arm_performance'], y=data_arm['arm_pkg_energy'], mode='lines+markers', name='ARM')





	layout_energy = go.Layout(title="Benchmark = " + Benchmark + "   Class = " + Class,

                   plot_bgcolor='rgb(230, 230, 230)', xaxis = dict(title = 'Thread'), yaxis = dict(title = 'Energy'))

	layout_time = go.Layout(title="Benchmark = " + Benchmark + "   Class = " + Class,

                   plot_bgcolor='rgb(230, 230, 230)', xaxis = dict(title = 'Thread'), yaxis = dict(title = 'Time'))

	layout_performance = go.Layout(title="Performanc/Power Consumption Profile for ARM and x86 \n" + Benchmark.upper() + " Class " + Class,

                   plot_bgcolor='rgb(230, 230, 230)', xaxis = dict(title = 'Performance (1/Time)'), yaxis = dict(title = 'Energy\n(Package)'))



	fig_energy = go.Figure(data=[trace1, trace2, trace3, trace4], layout=layout_energy)

	fig_time = go.Figure(data=[trace5, trace6], layout=layout_time)

	fig_performance = go.Figure(data=[trace7, trace8], layout=layout_performance)



	img_directory = "images/"

	if not os.path.exists(img_directory):

    		os.makedirs(img_directory)

	image_name_energy = img_directory + Benchmark +'.'+ Class +'.energy.png';

	image_name_time = img_directory + Benchmark +'.'+ Class +'.time.png';

	image_name_performance = img_directory + Benchmark +'.'+ Class +'.performance.png';



	py.image.save_as(fig_energy, image_name_energy)

	py.image.save_as(fig_time, image_name_time)

	py.image.save_as(fig_performance, image_name_performance)

	

	print("%s" % image_name_energy)

	print("%s" % image_name_time)

	print("%s" % image_name_performance)

#	from IPython.display import Image

#	Image(filename=image_name_energy) 

	

	

#Main

draw(parse_arguments().bench_name)


