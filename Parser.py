import math

class Parser:
	def __init__(self, probs, word_to_int1, word_to_int2, int_to_word1, int_to_word2):
		self.probs = probs
		self.word_to_int1 = word_to_int1
		self.word_to_int2 = word_to_int2
		self.int_to_word1 = int_to_word1
		self.int_to_word2 = int_to_word2

	# returns value > 1
	def conditional_prob(self, tree1, tree2):
		unk = '*UNK*'
		sent = [self.word_to_int1['*NULL*']]
		for token in tree1.tokens[1:]:
			word = tree1.tokens[token.head].pos + ' -> ' + token.pos
			if word not in self.word_to_int1:
				if token.pos not in self.word_to_int1:
					word = unk
				else:
					word = token.pos
			sent.append(self.word_to_int1[word])
			
		para = []
		for token in tree2.tokens[1:]:
			word = tree2.tokens[token.head].pos + ' -> ' + token.pos
			if word not in self.word_to_int2:
				if token.pos not in self.word_to_int2:
					word = unk
				else:
					word = token.pos
			para.append(self.word_to_int2[word])
			
		prob = 0
		unk = self.word_to_int2[unk]
		for f in para:
			x = 0
			for e in sent:
				if e in self.probs:
					if f in self.probs[e]:
						x += self.probs[e][f]
					elif unk in self.probs[e]:
						x += self.probs[e][unk]
					else:
						x += 10 ** -12 # hack
				else:
					#print 'wtf?'
					tmp = self.word_to_int1[unk]
					if f in self.probs[tmp]:
						x += self.probs[tmp][f]
					elif unk in self.probs[tmp]:
						x += self.probs[tmp][unk]
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
		tree1s = tree1s[:2]
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
			#print index, x, math.log(tree1_prob[1]), math.log(y), y
			index += 1
			if x > max_val2:
				max_val2 = x
				argmax = tree1
		#print

		return argmax
