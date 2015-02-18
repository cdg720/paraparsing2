from CoNLL import Corpus
from Analyzer import Analyzer
from EM import EM
from Parser import Parser
from Words import Words
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

# 0-index: 0 ROOT
def read_alignments(file):
	# 0: exact, 1: stem, 2: synonym, 3: paraphrase
	f = open(file, 'r')
	broken = []
	tmp = []
	count = 0
	for line in f.read().splitlines():
		if line == '':
			broken.append(tmp)
			tmp = []
			continue
		tmp.append(line)

	alignments = []
	for align in broken:
		len1 = len(align[1].split()) + 1
		len2 = len(align[2].split()) + 1
		align1 = [[-1,-1]] * len1
		align2 = [[-1,-1]] * len2
		for line in align[4:]:
			tokens = line.split() # every score = 1.0. seems weird and useless
			x = [int(tmp) for tmp in tokens[1].split(':')] # x -> y			
			y = [int(tmp) for tmp in tokens[0].split(':')] # y -> x
			# ignore aligned phrases (more than one word)
			if x[1] != 1 or y[1] != 1:
				continue
			align1[x[0]+1] = [y[0]+1, int(tokens[2])] # add one. ROOT is 0th word.
			align2[y[0]+1] = [x[0]+1, int(tokens[2])]
		alignments.append(align1)
		alignments.append(align2)
	return alignments

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
	if len(sys.argv) != 8:
		print 'usage: python foo.py train.gold train.sd205 train.probs train.align test.sd205 test.probs test.align'
		sys.exit(0)

	train_trees, train_probs = read_nbest(sys.argv[2], sys.argv[3]) 
	train_paras = train_trees[1::2] # n-best
	gold_sents = Corpus(sys.argv[1]).sentences[::2] # gold
	train_align = read_alignments(sys.argv[4]) # train.align

	# print train_align[0]
	# print len(train_align)
	# sys.exit(0)

	# print >> sys.stderr, 'start EM' 
	#em = EM(gold_sents[:10], train_paras[:10], train_probs[1::2][:10])

	tri = False
	targets = Words()
	paraphrases = Words()
	if tri:
		targets.preprocess2(gold_sents, with_null=True)
		paraphrases.preprocess2([x[0] for x in train_paras])
		print >> sys.stderr, 'USING TRIGRAMS'
	else:
		targets.preprocess(gold_sents, with_null=True)		
		paraphrases.preprocess([x[0] for x in train_paras])
		print >> sys.stderr, 'USING BIGRAMS'		

	alignment = True
	if alignment:
		print >> sys.stderr, 'WITH ALIGNMENTS'
	else:
		print >> sys.stderr, 'WITHOUT ALIGNMENTS'
	em = EM(targets.sents, paraphrases.sents, train_align[::2], train_align[1::2])
	em.run(cert=alignment)
	print >> sys.stderr, em.probs2
	#sys.exit(0)
	#em.sanity()

	# cheating	
	# print >> sys.stderr, 'start parsing' 
	# parser = Parser(em.probs, em.word_to_int1, em.word_to_int2)
	# for tree1s, tree1_probs, tree2s in zip(train_trees[::2], train_probs[::2], train_trees[1::2]):
	# 	print parser.parse(tree1s, tree1_probs, tree2s)
	# 	print tree2s[0]
	
	test_trees, test_probs = read_nbest(sys.argv[5], sys.argv[6])
	test_align = read_alignments(sys.argv[7]) # test.align

	print >> sys.stderr, 'start parsing'
	parser = Parser(em.probs, em.probs2, targets.word_to_int[targets.unk], paraphrases.word_to_int[paraphrases.unk])
	analyzer = Analyzer()
	for tree1s, tree1_probs, x_align, tree2s, y_align in zip(test_trees[::2], test_probs[::2], test_align[::2], test_trees[1::2], test_align[1::2]):
		if tri:
			index = parser.parse([targets.convert2(x, with_null=True) for x in tree1s], tree1_probs, [paraphrases.convert2(x) for x in tree2s], x_align, y_align, cert=alignment)
		else:
			index = parser.parse([targets.convert(x, with_null=True) for x in tree1s], tree1_probs, [paraphrases.convert(x) for x in tree2s], x_align, y_align, cert=alignment)
		#print index, len(tree1s), len(tree2s)
		# analyzer.analyze(targets.convert(tree1s[index[0]], with_null=True, inting=False), paraphrases.convert(tree2s[index[1]], with_null=False, inting=False))
		print tree1s[index[0]]
		print tree2s[index[1]]
	# analyzer.top_transformations()

main()
		
						 
