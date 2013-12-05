from worldgen.namegen import *

language = generate_language()
for i in xrange(10):
	print(language.name())