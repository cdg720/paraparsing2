import operator

class Analyzer:
	def __init__(self):
		self.probs = {}
		self.count = {}

	def analyze(self, target, paraphrase):
		for w1 in target:
			if w1 not in self.probs:
				self.probs[w1] = {}
				self.count[w1] = 1.
			else:
				self.count[w1] += 1
			for w2 in paraphrase:
				# if w1 == w2:
				# 	continue
				if w2 not in self.probs[w1]:
					self.probs[w1][w2] = 1.
				else:
					self.probs[w1][w2] += 1

	def top_transformations(self):
		sorted_y = sorted(self.count.items(), key=operator.itemgetter(1))
		sorted_y.reverse()

		for key1 in sorted_y:
			print key1
			key1 = key1[0]
			total = sum(self.probs[key1].values())
			for key2 in self.probs[key1]:
				self.probs[key1][key2] /= total
			sorted_x = sorted(self.probs[key1].items(), key=operator.itemgetter(1))
			sorted_x.reverse()
			for x in sorted_x[:10]:
				print x
			print
				
