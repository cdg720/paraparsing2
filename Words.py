''' Preprocess documents '''

class Words:
	def __init__(self):
		self.dictionary = {}
		self.null = '*NULL*'
		self.unk = '*UNK*'
		self.word_to_int = {}
		self.int_to_word = []
		self.sents = []

	def count(self, trees):
		for tree in trees:
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if word not in self.dictionary:
					self.dictionary[word] = 1
				else:
					self.dictionary[word] += 1
				if token.pos not in self.dictionary:
					self.dictionary[token.pos] = 1
				else:
					self.dictionary[token.pos] += 1

	def preprocess(self, trees, with_null=False):
		self.count(trees)

		if with_null:
			self.word_to_int[self.null] = len(self.word_to_int)
			self.int_to_word.append(self.null)
			
		for tree in trees:
			if with_null:
				sent = [self.word_to_int[self.null]] # NULL word
			else:
				sent = []
			for token in tree.tokens[1:]:
				word = tree.tokens[token.head].pos + ' -> ' + token.pos
				if self.dictionary[word] == 1: # unk rare words
					if self.dictionary[token.pos] <= 10:
						word = self.unk
					else:
						word = token.pos # back-off
				if word not in self.word_to_int:
					self.word_to_int[word] = len(self.word_to_int)
					self.int_to_word.append(word)
				sent.append(self.word_to_int[word])
			self.sents.append(sent)
	
