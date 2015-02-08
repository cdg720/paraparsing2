import math, operator, random, sys

class EM:
	probs = {}
	counts = {}
	word_to_int1 = {} # target sent, e
	word_to_int2 = {}	
	int_to_word1 = []
	int_to_word2 = []	
	
	def __init__(self, tree1s, tree2s):
		self.sents, self.paras = self.preprocess(tree1s, tree2s)
		self.em()

	# currently IBM model 1
	def em(self):
		self.init()
		max_iter = 10000
		prev = self.estep()
		self.mstep()
		for i in xrange(1, max_iter):
			print >> sys.stderr, i - 1, prev
			log_likelihood = self.estep()
			if abs(log_likelihood - prev) / abs(prev) < 0.001:
			#if abs(log_likelihood - prev) < 0.01:
				break
			self.mstep()
			prev = log_likelihood

	def estep(self):
		log_likelihood = 0
		for e in self.counts:
			for f in self.counts[e]:
				self.counts[e][f] = 0
		for para, sent in zip(self.paras, self.sents):
			for f in para:
				p_k = 0
				for e in sent:
					p_k += self.probs[e][f]
				log_likelihood += math.log(p_k)
				for e in sent:
					self.counts[e][f] += self.probs[e][f] / p_k
		return log_likelihood

	# TODO: how do i handle unks?
	def init(self):
		for para, sent in zip(self.paras, self.sents):		
			for f in para:
				for e in sent:
					if e not in self.probs:
						self.probs[e] = {}
						self.counts[e] = {}
					if f not in self.probs[e]:
						self.probs[e][f] = 1. + random.random() / 10
						self.counts[e][f] = 0.

	def mstep(self):
		for e in self.counts:
			z = sum(self.counts[e].values())
			for f in self.counts[e]:
				self.probs[e][f] = self.counts[e][f] / z

	def preprocess(self, tree1s, tree2s):
		null = '*NULL*'
		unk = '*UNK*'
		# process target trees
		tmp = {}
		for tree in tree1s:
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if word not in tmp:
					tmp[word] = 1
				else:
					tmp[word] += 1
				if token.pos not in tmp:
					tmp[token.pos] = 1
				else:
					tmp[token.pos] += 1

		# sorted_tmp = sorted(tmp.items(), key=operator.itemgetter(1))
		# for z in sorted_tmp:
		# 	if len(z[0].split('->')) == 0:
		# 		print z
	
		sents = []
		self.word_to_int1[null] = len(self.word_to_int1)
		self.int_to_word1.append(null)
		for tree in tree1s:
			sent = [self.word_to_int1[null]] # NULL word
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if tmp[word] == 1: # unk rare words
					if tmp[token.pos] <= 10:
						word = unk
					else:
						word = token.pos # back-off
				if word not in self.word_to_int1:
					self.word_to_int1[word] = len(self.word_to_int1)
					self.int_to_word1.append(word)
				sent.append(self.word_to_int1[word])
			sents.append(sent)

		# process papaphrase trees
		tree2s = [x[0] for x in tree2s] # first-best paraphrase
		tmp = {}
		for tree in tree2s:
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if word not in tmp:
					tmp[word] = 1
				else:
					tmp[word] += 1
				if token.pos not in tmp:
					tmp[token.pos] = 1
				else:
					tmp[token.pos] += 1

		# sorted_tmp = sorted(tmp.items(), key=operator.itemgetter(1))
		# for z in sorted_tmp:
		# 	if len(z[0].split('->')) == 1:
		# 		print z
		
		paras = []
		for tree in tree2s:
			para = [] # no NULL word
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if tmp[word] == 1:
					if tmp[token.pos] <= 10:
						word = unk
					else:
						word = token.pos # back-off
				if word not in self.word_to_int2:
					self.word_to_int2[word] = len(self.word_to_int2)
					self.int_to_word2.append(word)
				para.append(self.word_to_int2[word])
			paras.append(para)
		return sents, paras

	def sanity(self):
		for key in self.probs:
			print self.int_to_word1[key]
			sorted_x = sorted(self.probs[key].items(), key=operator.itemgetter(1))
			print [(self.int_to_word2[x[0]], x[1]) for x in sorted_x[-10:]]
			print 
