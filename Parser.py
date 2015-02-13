import math

class Parser:
	#def __init__(self, probs, word_to_int1, word_to_int2, int_to_word1, int_to_word2):
	def __init__(self, probs, unk1, unk2):
		self.probs = probs
		self.unk1 = unk1
		self.unk2 = unk2
		# self.word_to_int1 = word_to_int1
		# self.word_to_int2 = word_to_int2
		# self.int_to_word1 = int_to_word1
		# self.int_to_word2 = int_to_word2

	# returns value > 1
	def conditional_prob(self, tree1, tree2):
		sent = tree1
		para = tree2
		# sent = [self.word_to_int1['*NULL*']]
		# for token in tree1.tokens[1:]:
		# 	word = tree1.tokens[token.head].pos + ' -> ' + token.pos
		# 	if word not in self.word_to_int1:
		# 		if token.pos not in self.word_to_int1:
		# 			word = unk
		# 		else:
		# 			word = token.pos
		# 	sent.append(self.word_to_int1[word])
			
		# para = []
		# for token in tree2.tokens[1:]:
		# 	word = tree2.tokens[token.head].pos + ' -> ' + token.pos
		# 	if word not in self.word_to_int2:
		# 		if token.pos not in self.word_to_int2:
		# 			word = unk
		# 		else:
		# 			word = token.pos
		# 	para.append(self.word_to_int2[word])
			
		prob = 0
		for f in para:
			x = 0
			for e in sent:
				if e in self.probs:
					if f in self.probs[e]:
						x += self.probs[e][f]
					elif self.unk2 in self.probs[e]:
						x += self.probs[e][self.unk2]
					else:
						x += 10 ** -12 # hack
				else:
					if f in self.probs[self.unk1]:
						x += self.probs[self.unk1][f]
					elif self.unk2 in self.probs[self.unk1]:
						x += self.probs[self.unk1][self.unk2]
					else:
						x += 10 ** -12				
			prob += math.log(x) # looks problematic
		# if prob > 1:
		# 	print [self.int_to_word1[e] for e in sent]
		# 	print [self.int_to_word2[f] for f in para]
		# 	print
		return prob

	def parse(self, tree1s, tree1_probs, tree2s):
		# hack
		tree1s = tree1s
		#tree2s = tree2s[:5]
		max_val = -999999 # -inf
		for tree1, tree1_prob in zip(tree1s, tree1_probs):
			for tree2 in tree2s:
				x = self.conditional_prob(tree1, tree2)
				if x > max_val:
					max_val = x

		max_val2 = -999999 # -inf
		argmax = None
		index = 0
		for tree1, tree1_prob in zip(tree1s, tree1_probs):
			x = math.log(tree1_prob[1]) # reranker prob
			y = 0
			for tree2 in tree2s:
				z = self.conditional_prob(tree1, tree2)
				y += math.exp(z-max_val)
			x += math.log(y)
			if x > max_val2:
				max_val2 = x
				argmax = index
			index += 1

		return argmax
