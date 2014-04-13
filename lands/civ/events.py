import random

class Event:
	
	def rate(self,crowded):
		if crowded and self.max>100:
			return random.randint(self.min-4,(self.max+200)/3)
		else:
			return random.randint(self.min,self.max)

class Plague(Event):

	def __init__(self):
		self.min = 45
		self.max = 90

class Famine(Event):

	def __init__(self):
		self.min = 80
		self.max = 98

class Grow(Event):

	def __init__(self):
		self.min = 101
		self.max = 110
