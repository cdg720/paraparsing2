import math, sys

class Parser:
	def __init__(self, probs, unk1, unk2):
		self.probs = probs
		self.unk1 = unk1
		self.unk2 = unk2
		self.weight = 10
		self.n = 2
		print >> sys.stderr, 'WEIGHT:', self.weight
		print >> sys.stderr, 'FIRST', self.n

	# without alignment
	def conditional_prob(self, tree1, tree2):
		sent = tree1
		para = tree2

		log_prob = 0
		for f in para:
			x = 0
			for e in sent:
				if e in self.probs:
					if f in self.probs[e]:
						x += self.probs[e][f]
					elif self.unk2 in self.probs[e]:
						x += self.probs[e][self.unk2]
					else:
						# TODO: do some kind of smoothing
						x += 10 ** -12 # hack
				else:
					if f in self.probs[self.unk1]:
						x += self.probs[self.unk1][f]
					elif self.unk2 in self.probs[self.unk1]:
						x += self.probs[self.unk1][self.unk2]
					else:
						x += 10 ** -12				
			log_prob += math.log(x) # looks problematic
		return log_prob

	# returns value > 1, which is normal
	def conditional_prob2(self, tree1, tree2, x_to_y):
		sent = tree1
		para = tree2

		# print tree1, len(tree1)
		# print tree2, len(tree2)
		# print x_to_y, len(x_to_y)
		certainty = 0.9
		log_prob = 0
		for i, f in enumerate(para):
			x = 0
			for j, e in enumerate(sent):
				if e in self.probs:
					if f in self.probs[e]:
						if x_to_y[j][0] == i+1:
							x += self.probs[e][f] * certainty
						else:
							x += self.probs[e][f] * (1 - certainty)
					elif self.unk2 in self.probs[e]:
						if x_to_y[j][0] == i+1:
							x += self.probs[e][self.unk2] * certainty
						else:
							x += self.probs[e][self.unk2] * (1 - certainty)
					else:
						if x_to_y[j][0] == i+1:
							x += 10 ** -12 * certainty
						else:
							x += 10 ** -12 * (1 - certainty)# hack
				else:
					if f in self.probs[self.unk1]:
						if x_to_y[j][0] == i+1:
							x += self.probs[self.unk1][f] * certainty
						else:
							x += self.probs[self.unk1][f] * (1 - certainty)
					elif self.unk2 in self.probs[self.unk1]:
						if x_to_y[j][0] == i+1:
							x += self.probs[self.unk1][self.unk2] * certainty
						else:
							x += self.probs[self.unk1][self.unk2] * (1 - certainty)
					else:
						if x_to_y[j][0] == i+1:
							x += 10 ** -12 * certainty
						else:
							x += 10 ** -12 * (1 - certainty)
			log_prob += math.log(x) # looks problematic
		return log_prob

	def parse(self, tree1s, tree1_probs, tree2s, x_to_y, y_align, cert=False):
		# hack
		tree1s = tree1s[:self.n]
		#tree2s = tree2s[:5]
		max_val = -999999 # -inf
		for tree1, tree1_prob in zip(tree1s, tree1_probs):
			for tree2 in tree2s:
				if cert:
					x = self.conditional_prob2(tree1, tree2, x_to_y)
				else:
					x = self.conditional_prob(tree1, tree2)
				if x > max_val:
					max_val = x

		max_val2 = -999999 # -inf
		argmax = None
		index = 0
		# TODO: CHECK IF THE FOLLOWING IS CORRECT
		for tree1, tree1_prob in zip(tree1s, tree1_probs):
			x = math.log(tree1_prob[1]) * self.weight # reranker prob
			y = 0
			for tree2 in tree2s:
				if cert:
					z = self.conditional_prob2(tree1, tree2, x_to_y)
				else:
					z = self.conditional_prob(tree1, tree2)
				y += math.exp(z-max_val)
			x += math.log(y)
			if x > max_val2:
				max_val2 = x
				argmax = index
			index += 1

		return argmax
