#!/usr/bin/env python
from __future__ import division
import random
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats

class Neutron():
	def __init__(self, grid, data, birth_cpdf):
		self.group = 1
		self.df = grid
		self.xs = data
		self.birth_cpdf = birth_cpdf
		
		self.cell = self.sample_birth_cell()
		self.location = (self.cell * spacing)+(random.random() * spacing)
		self.direction = 2 * random.random() - 1
		
		

	def update_cell(self):
		self.cell = int(self.location/spacing)
		
	def sample_birth_cell(self):
		cell_sample = random.random()
		for i, sample in enumerate(self.birth_cpdf):

			if cell_sample < sample:
				return (i-1)
	
	def scatter(self):
		self.direction = 2 * random.random() - 1


	def distance(self, material):
		if self.group == 1:
			return abs(np.log(random.random())/self.xs.loc[material, 'sigma_t1'])
		else:
			return abs(np.log(random.random())/self.xs.loc[material, 'sigma_t2'])
			 

	def interaction(self):
		self.update_cell()
		material = self.df.iloc[self.cell, 1]
		
		sigma_t1 = self.xs.loc[material, 'sigma_t1']
		sigma_s11 = self.xs.loc[material, 'sigma_s11']
		sigma_t2 = self.xs.loc[material, 'sigma_t2']
		sigma_s22 = self.xs.loc[material, 'sigma_s22']


		if self.group == 1:
			if random.random()  <= (sigma_s11/sigma_t1): 
				self.scatter()
				return 's11'

			else:
				self.group = 2
				self.scatter()
				return 's12'
				
		if self.group == 2:
			if random.random() <= (sigma_s22/sigma_t2):
				self.scatter()
				return 's22'
					
			else: 
				return 'fission'



	def move(self):
		while True:
			self.update_cell()
			material = self.df.iloc[self.cell, 1]
			
			s = self.distance(material)
			
			#print(self.location)
			
			right_cell_pos = self.cell * spacing + spacing
			left_cell_pos = self.cell * spacing
				
			if self.direction > 0:
				possible_location = self.direction * s + self.location

					
				if possible_location > right_cell_pos: 
					delta_x = right_cell_pos - self.location
					traveled = delta_x / self.direction
					self.location = right_cell_pos + 0.0001
						
					if self.location > 20.0:
						self.direction = - self.direction
						self.location = 19.9999
					yield ((self.cell, traveled), self.group)
						
					#if it is within the cell
				else:
					self.location = possible_location
					yield  ((self.cell, s), self.group)
					break
					

			# if is traveling in the negative direction
			if self.direction < 0:
				possible_location = self.location + (self.direction * s)
					
				if possible_location < left_cell_pos:
					delta_x = self.location - left_cell_pos
					traveled = abs(delta_x/self.direction)
					self.location = left_cell_pos - 0.0001
						
					if self.location < 0.0:
						self.direction = - self.direction
						self.location = 0.0001
					yield  ((self.cell, traveled), self.group)
						

				else:
					self.location = possible_location
					yield  ((self.cell, s), self.group)
					break

def initialize_fissionSource(grid, xs): # assumes uniform flux
	fission_sourceF = []
	for material in grid['material']:
		nu2 = xs.loc[material, 'nu2']
		sigma_f2 = xs.loc[material, 'sigma_f2']
		fission_sourceF.append(nu2 * sigma_f2)
	return np.asarray(fission_sourceF)
	
def generate_cpdf(fission_source):
	F_normed = fission_source * spacing / sum(fission_source * spacing)
	cpdf = []
	for i in range(128):
		cpdf.append(sum(F_normed[:i]))
	#cpdf = np.asarray(cpdf)
	return cpdf
	

	

global spacing
spacing = 0.15625

generations = 1
neutrons = 10000

k0 = 1


k = []
F = []

weight = 1


grid = pd.read_csv('grid.csv')
xs = pd.read_csv('XS.csv', index_col = 'material')
F0 = initialize_fissionSource(grid, xs)
cpdf = generate_cpdf(F0)
n = Neutron(grid, xs, cpdf)

for i in range(generations):
	flux_1 = np.zeros(128)
	flux_2 = np.zeros(128)
	for i in range(neutrons):
			n = Neutron(grid, xs, cpdf)
			while True:
				
				#move unitll interaction occurs
				for track_data in n.move():
					cell = track_data[0][0]
					track = track_data[0][1]
					group = track_data[1]
					
					if group == 1:
						flux_1[cell] = flux_1[cell] + (track * weight) / (neutrons * spacing)
					if group == 2:
						flux_2[cell] = flux_2[cell] + (track * weight) / (neutrons * spacing)
						
				#what kind of interaction
				interaction = n.interaction()
				if interaction == 'fission':
					print('fission')
					break
					
	Fn = flux_2 * F0	
	F_normed = Fn * spacing/ sum(Fn * spacing)
	kn = k0 * sum(Fn * spacing)
		
	#hist_dist = scipy.stats.rv_histogram(F_normed)

				
plt.plot(flux_1)
plt.plot(flux_2)
plt.show()
			