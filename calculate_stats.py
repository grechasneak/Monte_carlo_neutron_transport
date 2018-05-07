#!/usr/bin/env python
from __future__ import division
import random
import math
import numpy as np



def process_statistics(F):
	Flux1 = np.zeros(128)
	Flux2 = np.zeros(128)
	Flux1_squared = np.zeros(128)
	Flux2_squared = np.zeros(128)
	Current1 = np.zeros(129)
	Current2 = np.zeros(129)
	Current1_squared = np.zeros(129)
	Current2_squared = np.zeros(129)
	
	for data in F:
		flux_1 = data[0]
		flux_2 = data[1]
		flux1_squared = data[2]
		flux2_squared = data[3]
		current1 = data[4]
		current2 = data[5]
		
		Flux1 +=  flux_1
		Flux2 +=  flux_2 
		Flux1_squared += flux1_squared
		Flux2_squared += flux2_squared
		Current1 += current1
		Current2 += current2
		Current1_squared += current1**2
		Current2_squared += current2**2
		
	total_neutrons = (len(F) * neutrons)
	
	Flux1_average = Flux1 / total_neutrons
	Flux1_var = np.sqrt((1 / (total_neutrons - 1) * (Flux1_squared - Flux1_average**2))/total_neutrons)
	
	Current1_average = Current1 / total_neutrons
	Current1_var = np.sqrt((1 / (total_neutrons - 1) * (Current1_squared - Current1_average**2))/total_neutrons)
	
	Flux2_average = Flux2 / total_neutrons
	Flux2_var = np.sqrt((1 / (total_neutrons - 1) * (Flux2_squared - Flux2_average**2))/total_neutrons)
	
	Current2_average = Current2 / total_neutrons
	Current2_var = np.sqrt((1 / (total_neutrons - 1) * (Current2_squared - Current2_average**2))/total_neutrons)
	
	return Flux1_average, Flux1_var, Flux2_average, Flux2_var, Current1_average, Current1_var, Current2_average, Current2_var
	


