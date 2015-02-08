from CoNLL import Corpus
from EM import EM
from Parser import Parser
import gzip, math, sys

def normalize(probs):
	first = probs[0] # parser, reranker
	z1, z2 = 0, 0
	p = []

	# sum probs
	for prob in probs:
		z1 += 2 ** (prob[0] - first[0])
		z2 += math.exp(prob[1] - first[1])

	# normalize them
	for prob in probs:
		p.append( (2 ** (prob[0] - first[0]) / z1, math.exp(prob[1] - first[1]) / z2) )

	return p 

def read_nbest(trees_file, probs_file):
	corpus = Corpus(trees_file)
	f = gzip.open(probs_file, 'rb')
	
	trees, probs = [], []
	t, p = [], []

	index = 0
	count = 0
	for line in f.read().splitlines():
		if count == 0:
			count = int(line)
			if p:
				trees.append(t)
				probs.append(normalize(p))
				t, p = [], []
			continue
		tokens = line.split('\t')
		if len(tokens) != 2:
			print 'Wrong Format'
			print line
			sys.exit(0)

		p.append( (float(tokens[0]), float(tokens[1])) )
		t.append(corpus.sentences[index])
		index += 1
		count -= 1

	if p:
		probs.append(normalize(p))
		trees.append(t)
		
	return trees, probs

def main():
	if len(sys.argv) != 6:
		print 'usage: python foo.py train.gold train.sd205 train.probs test.sd205 test.probs'
		sys.exit(0)
	#sys.argv = ['foo.py' 'data/train.gold' 'data/train.sd205.gz' 'data/train.probs.gz' 'data/test.sd205.gz' 'data/test.probs.gz']

	train_trees, train_probs = read_nbest(sys.argv[2], sys.argv[3]) 
	train_paras = train_trees[1::2] # n-best
	gold_sents = Corpus(sys.argv[1]).sentences[::2] # gold	

	em = EM(gold_sents, train_paras)
	#em.sanity()

	# cheating	
	# print >> sys.stderr, 'start parsing' 
	# parser = Parser(em.probs, em.word_to_int1, em.word_to_int2)
	# for tree1s, tree1_probs, tree2s in zip(train_trees[::2], train_probs[::2], train_trees[1::2]):
	# 	print parser.parse(tree1s, tree1_probs, tree2s)
	# 	print tree2s[0]
	
	test_trees, test_probs = read_nbest(sys.argv[4], sys.argv[5])

	print >> sys.stderr, 'start parsing'
	parser = Parser(em.probs, em.word_to_int1, em.word_to_int2, em.int_to_word1, em.int_to_word2)
	for tree1s, tree1_probs, tree2s in zip(test_trees[::2], test_probs[::2], test_trees[1::2]):
		print parser.parse(tree1s, tree1_probs, tree2s)
		print tree2s[0]

main()
		
						 