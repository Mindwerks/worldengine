from os import listdir
from os.path import isfile, join
import random
import itertools

def lang_samples(path='lang_samples'):
	lang_files = [ f for f in listdir(path) if isfile(join(path,f)) ]
	lang_samples = {}
	for lf in lang_files:
		with open(join(path,lf)) as f:
			content = f.readlines()
		lang_samples[lf[0:-4]] = content
	return lang_samples

class Language:

	def __init__(self,syllables, starts, ends, combinations):
		self.syllables = syllables
		self.starts = starts
		self.ends = ends
		self.combinations = combinations
		self.min_syl = 2
		self.max_syl = 4

	def name(self):
		#random number of syllables, the last one is always appended
		num_syl = random.randint(self.min_syl, self.max_syl - 1)
		
		#turn ends list of tuples into a dictionary
		ends_dict = dict(self.ends)
		
		#we may have to repeat the process if the first "min_syl" syllables were a bad choice
		#and have no possible continuations; or if the word is in the forbidden list.
		word = []; word_str = ''
		while len(word) < self.min_syl:
			#start word with the first syllable
			syl = self._select_syllable(self.starts, 0)
			word = [self.syllables[syl]]
			
			for i in range(1, num_syl):
				#don't end yet if we don't have the minimum number of syllables
				if i < self.min_syl: end = 0
				else: end = ends_dict.get(syl, 0)  #probability of ending for this syllable
				
				#select next syllable
				syl = self._select_syllable(self.combinations[syl], end)
				if syl is None: break  #early end for this word, end syllable was chosen
				
				word.append(self.syllables[syl])
				
			else:  #forcefully add an ending syllable if the loop ended without one
				syl = self._select_syllable(self.ends, 0)
				word.append(self.syllables[syl])
			
			word_str = ''.join(word)
				
		return word_str.capitalize()

	def _select_syllable(self,counts, end_count):
		if len(counts) == 0: return None  #no elements to choose from
		
		#"counts" holds cumulative counts, so take the last element in the list
		#(and 2nd in that tuple) to get the sum of all counts
		chosen = random.randint(0, counts[-1][1] + end_count)
		
		for (syl, count) in counts:
			if count >= chosen:
				return syl
		return None

def generate_random_language_sample():
	samples = lang_samples()
	lang_a = random.choice(samples.keys())
	lang_b = random.choice(samples.keys())
	#print('Mixing %s and %s' % (lang_a,lang_b))
	SAMPLE_SIZE = 100
	n_a = random.randint(0,SAMPLE_SIZE)
	n_b = SAMPLE_SIZE-n_a 
	#print('Proportion: %i and %i' % (n_a,n_b))
	sample = []
	for i in xrange(n_a):
		sample.append(random.choice(samples[lang_a]).lower().strip())
	for i in xrange(n_b):
		sample.append(random.choice(samples[lang_b]).lower().strip())
	return sample

def get_count(count_tuple):
	return count_tuple[1]

def get_best_syllables(num_letters, fraction, sample):
	alphabet = [chr(i) for i in range(ord('a'), ord('z') + 1)]
	
	#get all possible syllables using this number of letters, then count
	#them in the sample. output is list of tuples (syllable, count).
	counts = [(''.join(letters), sample.count(''.join(letters)))
		for letters in itertools.product(alphabet, repeat = num_letters)]
	
	#output to comma-separated-values file (view in Excel), useful to figure out fraction parameters.
	#print counts, len(counts)
	#with open('counts.csv','w') as f:
	#	f.write(''.join([str(count_tuple[1]) + '\n' for count_tuple in counts]))
	
	#get only the syllables with the most counts, up to the fraction specified
	counts = [ (l,c) for l,c in counts if c>0 ]
	counts.sort(key = get_count)
	n = int(fraction * len(counts))
	counts = counts[-n:]
	
	#get syllables from the tuples by "unzipping"
	syllables = list(zip(*counts)[0])
	return syllables

def count_combinations(syllables, sample):	
	combinations = []
	for prefix in syllables:
		combinations.append(count_with_prefix(syllables, prefix, sample))
	
	starts = count_with_prefix(syllables, ' ', sample)
	ends = count_with_postfix(syllables, ' ', sample)
	
	return (combinations, starts, ends)

def count_with_prefix(syllables, prefix, sample):
	combinations = []
	total = 0
	for (index, syl) in enumerate(syllables):
		count = sample.count(prefix + syl)
		if count != 0:
			total += count
			combinations.append([index, total])
	return combinations

def count_with_postfix(syllables, postfix, sample):
	combinations = []
	total = 0
	for (index, syl) in enumerate(syllables):
		count = sample.count(syl + postfix)
		if count != 0:
			total += count
			combinations.append([index, total])
	return combinations

def produce_language(sample,frac_2s=0.2,frac_3s=0.05):
	sample = ' '+' '.join(sample)+ ' '
	syllables = get_best_syllables(2, frac_2s, sample)

	#optionally, do the same with 3 letters syllables (slower)
	syllables.extend(get_best_syllables(3, frac_3s, sample))
	(combinations, starts, ends) = count_combinations(syllables, sample)
	language = Language(syllables,starts,ends,combinations)
	return language

def generate_language():
	sample = generate_random_language_sample()
	language = produce_language(sample)
	return language
	