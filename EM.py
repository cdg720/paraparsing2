import math, operator, random, sys

class EM:
	probs = {}
	counts = {}

	def __init__(self, sents, paras):
		self.sents = sents
		self.paras = paras

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

	# IBM model 1
	def run(self):
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
			
	# def sanity(self):
	# 	for key in self.probs:
	# 		print self.int_to_word1[key]
	# 		sorted_x = sorted(self.probs[key].items(), key=operator.itemgetter(1))
	# 		print [(self.int_to_word2[x[0]], x[1]) for x in sorted_x[-10:]]
	# 		print 
