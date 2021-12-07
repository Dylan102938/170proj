import random

def writeInput():
	with open('inputs/200.in', 'w') as f:
		for i in range(1, 201):
			f.write(str(i) + " " + str(random.randint(1, 1440)) + " " + str(random.randint(1, 60)) + " " + str(round(random.uniform(0.1, 99.9), 2)) + '\n')
		f.close()
	# with open('outputs/100_optimal.out', 'w') as f:
	# 	for i in range(150, -1, -1):
	# 		f.write(str(i) + '\n')	
writeInput()
