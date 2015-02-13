''' Preprocess documents '''
import sys

class Words:
	def __init__(self):
		self.dictionary = {}
		self.null = '*NULL*'
		self.unk = '*UNK*'
		self.word_to_int = {}
		self.int_to_word = []
		self.sents = []

	def convert2(self, tree, with_null=False):
		sent = []
		if with_null:
			sent.append(self.word_to_int[self.null])
		for token in tree.tokens[1:]:
			if token.head == 0: # ROOT:
				word = 'GRAN' + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos
			else:
				word = tree.tokens[tree.tokens[token.head].head].pos + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos

			bigram = tree.tokens[token.head].pos + ' -> ' + token.pos
			if word not in self.word_to_int:
				if bigram not in self.word_to_int:
					if token.pos not in self.word_to_int:
						word = self.unk
					else:
						word = token.pos
				else:
					word = bigram
			sent.append(self.word_to_int[word])
		return sent

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

	def count2(self, trees):
		for tree in trees:
			for token in tree.tokens[1:]:
				# trigram counts
				if token.head == 0: # ROOT:
					trigram = 'GRAN' + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos
				else:
					trigram = tree.tokens[tree.tokens[token.head].head].pos + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos
				if trigram not in self.dictionary:
					self.dictionary[trigram] = 1
				else:
					self.dictionary[trigram] += 1

				# bigram counts
				bigram = tree.tokens[token.head].pos + ' -> ' + token.pos
				if bigram not in self.dictionary:
					self.dictionary[bigram] = 1
				else:
					self.dictionary[bigram] += 1

				# unigram counts
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
	
	def preprocess2(self, trees, with_null=False):
		self.count2(trees)

		if with_null:
			self.word_to_int[self.null] = len(self.word_to_int)
			self.int_to_word.append(self.null)
			
		for tree in trees:
			if with_null:
				sent = [self.word_to_int[self.null]] # NULL word
			else:
				sent = []
			for token in tree.tokens[1:]:
				# trigram counts
				if token.head == 0: # ROOT:
					word = 'GRAN' + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos
				else:
					word = tree.tokens[tree.tokens[token.head].head].pos + ' -> ' + tree.tokens[token.head].pos + ' -> ' + token.pos

				bigram = tree.tokens[token.head].pos + ' -> ' + token.pos
				if self.dictionary[word] == 1:
					if self.dictionary[bigram] == 1:
						if self.dictionary[token.pos] <= 10:
							word = self.unk
						else:
							word = token.pos
					else:
						word = bigram
						
				if word not in self.word_to_int:
					self.word_to_int[word] = len(self.word_to_int)
					self.int_to_word.append(word)
				sent.append(self.word_to_int[word])
			self.sents.append(sent)
