
import re
import itertools
import numpy as np

class CellData():
	def __init__(self, file):
		with open(file, 'r') as f: 
			data = f.readlines()
			list = []
			for line in data:
				numbers = line[:33]
				numbers = re.findall(r'[-+]?[0-9]*\.?[0-9]+', numbers)
				numbers = [float(i) for i in numbers]
				list.append(numbers)
				
			data = list[1:]
			data = [data[i] + data[i+1] for i in range(0,len(data),2)]
			data = np.asarray(data)
			self.data = data
		

		
matrix = CellData('sample.in').data
print(matrix)

