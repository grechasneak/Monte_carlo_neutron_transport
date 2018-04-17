#!/usr/bin/env python
from __future__ import division
import random
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Neutron():
	def __init__(self, grid, data):
		self.group = 1
		self.birth = 20*random.random()
		self.location = self.birth
		self.direction = 2 * random.random() - 1
		self.update_cell()
		self.df = grid
		self.xs = data
		
	def update_cell(self):
		self.cell = int(self.location/spacing)
		
	def scatter(self):
		self.direction = 2 * random.random() - 1

	def crossection(self, material, interaction):
		return self.xs.ix[material, interaction]
		

	def distance(self, material):
		if self.group == 1:
			return abs(np.log(random.random())/self.crossection(material, 'sigma_t1'))
		else:
			return abs(np.log(random.random())/self.crossection(material, 'sigma_t2'))
			 

	def interaction(self):
		while True:
			self.update_cell()

			material = self.df.ix[self.cell, 1]

			sigma_t1 = self.crossection(material, 0)
			sigma_s11 = self.crossection(material, 1)
			sigma_t2 = self.crossection(material, 3)
			sigma_s22 = self.crossection(material, 4)

			cell, track = self.move()
			
			
			if self.group == 1:
				if random.random()  <= (sigma_s11/sigma_t1): #is it within group?
					yield ((cell, track), self.group)

				# down scatter
				else:
					self.group = 2
					yield ((cell, track), self.group)

			if self.group == 2:
				if random.random() <= (sigma_s22/sigma_t2): #does it scatter or fission?
					# scatter
					yield ((cell, track), self.group)

				# fission
				else:
					#print('fission')
					yield ((cell, track), self.group)
					break




	def move(self):
		material = self.df.ix[self.cell, 1]
		s = self.distance(material)
		print(self.location)
		
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
					
				self.update_cell()	
				return self.cell, traveled
					
				#if it is within the cell
			else:
				self.location = possible_location
				self.scatter()
				return self.cell, s


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
					
				self.update_cell()	
				return self.cell, traveled
					
			#still within the cell
			else:
				self.location = possible_location
				self.scatter()
				return self.cell, s



global spacing
spacing = 0.15625

generations = 1
neutrons = 100

k0 = 1
F0 = 1

k = []
F = []

weight = 1


grid = pd.read_csv('grid.csv')
xs = pd.read_csv('XS.csv', index_col = 'material')

n = Neutron(grid, xs)

flux_1 = np.zeros(129)
flux_2 = np.zeros(129)
n = Neutron(grid, xs)
# for i in range(generations):

	# for i in range(neutrons):
			# n = Neutron(grid, xs)
			# for track_data in n.interaction():

				# cell = track_data[0][0]
				# track = track_data[0][1]
				# group = track_data[1]

				# if group == 1:
					# flux_1[cell] = flux_1[cell] + (track * weight) / (neutrons * spacing)
				# if group == 2:
					# flux_2[cell] = flux_2[cell] + (track * weight) / (neutrons * spacing)

				# #print(track)
