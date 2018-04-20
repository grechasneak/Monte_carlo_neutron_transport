#!/usr/bin/env python
from __future__ import division
import random
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Neutron():
	def __init__(self, grid, data, birth_cpdf):
		self.group = 1
		self.df = grid
		self.xs = data
		self.birth_cpdf = birth_cpdf
		
		self.cell = self.sample_birth_cell()
		self.location = (self.cell * spacing) + (random.random() * spacing)
		self.direction = 2 * random.random() - 1
		

	def update_cell(self):
		self.cell = int(self.location/spacing)
		
	def sample_birth_cell(self):
		'''
		Searches through the cpdf for the first value that is larger than the random number.
		The index of the number before the larger value is the birth cell.
		'''
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
		'''
		Generator function that moves the neutron untill it stops in a cell.
		Each time the neutron crosses a cell boudary or reaches the problem
		boundary the function yields the cell, track in that cell, and group of the neutron. 
		'''
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
					self.location = right_cell_pos + 0.001
						
					if self.location > 20.0:
						self.direction = - self.direction
						self.location = 19.999
						
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
					self.location = left_cell_pos - 0.001
						
					if self.location < 0.0:
						self.direction = - self.direction
						self.location = 0.001
					yield  ((self.cell, traveled), self.group)
						
				else:
					self.location = possible_location
					yield  ((self.cell, s), self.group)
					break

def gen_fissionSource(grid, xs, flux): 
	fission_sourceF = []
	for material in grid['material']:
		nu2 = xs.loc[material, 'nu2']
		sigma_f2 = xs.loc[material, 'sigma_f2']
		fission_sourceF.append(nu2 * sigma_f2)
	return np.asarray(fission_sourceF) * flux
	
def generate_cpdf(fission_source):
	F_normed = fission_source * spacing / sum(fission_source * spacing)
	cpdf = []
	for i in range(128):
		cpdf.append(sum(F_normed[:i]))
	#cpdf = np.asarray(cpdf)
	return cpdf
	
def tally_current(cells):
	current_tally = []
	try:
		for i in range(len(cells)):
			if cells[i] < cells[i + 1]:
				current_tally.append((cells[i], 1))
			
			if cells[i] > cells[i + 1]:
				current_tally.append((cells[i + 1], -1))
	except:	
		return current_tally
	
def process_statistics(F):
	Flux1 = np.zeros(128)
	Flux2 = np.zeros(128)
	Flux1_squared = np.zeros(128)
	Flux2_squared = np.zeros(128)
	for data in F:
		flux_1 = data[0]
		flux_2 = data[1]
		flux1_squared = data[2]
		flux2_squared = data[3]
		
		Flux1 = Flux1 + flux_1
		Flux2 = Flux2 + flux_2 
		Flux1_squared = Flux1_squared + flux1_squared
		Flux2_squared = Flux2_squared + flux2_squared
		
	total_neutrons = (len(F) * neutrons)
	
	Flux1_average = Flux1 / total_neutrons
	var1 = np.sqrt((1 / (total_neutrons - 1) * (Flux1_squared - Flux1_average**2))/total_neutrons)
	
	Flux2_average = Flux2 / total_neutrons
	var2 = np.sqrt((1 / (total_neutrons - 1) * (Flux2_squared - Flux2_average**2))/total_neutrons)
	return Flux1_average, Flux2_average, var1, var2
	
	

global spacing
spacing = 0.15625

generations = 5
neutrons = 100



grid = pd.read_csv('grid.csv')
xs = pd.read_csv('XS.csv', index_col = 'material')

F0 = gen_fissionSource(grid, xs, np.ones(128)) #initialize the values for F
cpdf = generate_cpdf(F0)

kn = 1
weight = 1

F = []
k = []
currents = []
for i in range(generations):
	flux_1 = np.zeros(128)
	flux_2 = np.zeros(128)
	flux1_squared = np.zeros(128)
	flux2_squared = np.zeros(128)
    
	current1 = np.zeros(127)
	current2 = np.zeros(127)
   
	for i in range(neutrons):
			cells = []
			n = Neutron(grid, xs, cpdf)
			while True:
				
				#move unitll interaction occurs
				for track_data in n.move():
					cell = track_data[0][0]
					track = track_data[0][1]
					group = track_data[1]
					
					cells.append(cell)
					if group == 1:
						flux_1[cell] = flux_1[cell] + (track * weight) / (neutrons * spacing)
						flux1_squared[cell] = flux1_squared[cell] + ((track * weight) / (neutrons * spacing))**2
						
						try:
							if n.direction > 0:
								current1[cell] = current1[cell] + 1
							else: # negative direction
								current1[cell - 1] = current1[cell - 1] - 1
						except:
							continue
							
					if group == 2:
						flux_2[cell] = flux_2[cell] + (track * weight) / (neutrons * spacing)
						flux2_squared[cell] = flux2_squared[cell] + ((track * weight) / (neutrons * spacing))**2
						
						try:
							if n.direction > 0:
								current2[cell] = current2[cell] + 1
							
							else: # negative direction
								current2[cell - 1] = current2[cell - 1] - 1
								
						except:
							continue
							
				#what kind of interaction
				interaction = n.interaction()
				if interaction == 'fission':
					print('fission', i)
					break
					
	fissions = gen_fissionSource(grid, xs, flux_2)	
	kn = spacing * sum(fissions)  * kn
	currents.append((current1, current2))
	F.append((flux_1, flux_2, flux1_squared, flux2_squared))
	k.append(kn)
	#print(kn)
	weight = 1 / kn
	cpdf = generate_cpdf(fissions)



mu1, mu2, std1, std2 = process_statistics(F)	
plt.plot(range(len(mu1)), mu1)
plt.fill_between(range(len(mu2)), mu2 - std2, mu2 + std2)
plt.fill_between(range(len(mu1)), mu1 - std1, mu1 + std1)
plt.show()
			

		
