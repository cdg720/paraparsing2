import math, operator, random, sys

class EM:
	probs = {}
	counts = {}

	def __init__(self, sents, paras, x_to_y, y_to_x):
		self.sents = sents
		self.paras = paras
		self.x_to_y = x_to_y # x: sent, y: para
		self.y_to_x = y_to_x

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

	# with alignments. I THINK THERE IS A BUG.
	def estep2(self):
		certainty = 0.9
		log_likelihood = 0
		for e in self.counts:
			for f in self.counts[e]:
				self.counts[e][f] = 0
		for para, sent, x_to_y2 in zip(self.paras, self.sents, self.x_to_y):
			for i, f in enumerate(para):
				p_k = 0
				for j, e in enumerate(sent):
					if x_to_y2[j][0] == i+1:
						p_k += self.probs[e][f] * certainty
					else:
						p_k += self.probs[e][f] * (1 - certainty)
				log_likelihood += math.log(p_k)
				for j, e in enumerate(sent):
					if x_to_y2[j][0] == i+1:
						self.counts[e][f] += self.probs[e][f] * certainty / p_k
					else:
						self.counts[e][f] += self.probs[e][f] * (1 - certainty) / p_k
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
	def run(self, cert=False):
		self.init()
		max_iter = 10000
		if cert:
			prev = self.estep2()
		else:
			prev = self.estep()
		self.mstep()
		for i in xrange(1, max_iter):
			print >> sys.stderr, i - 1, prev
			if cert:
				log_likelihood = self.estep2()
			else:
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
