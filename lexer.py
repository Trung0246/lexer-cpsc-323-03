from csv import writer as csv_writer
import regex
import sys

keyword = set(["if", "else", "while", "for", "func", "return"])
token = {
	"keyword": "keyword",
	"separator": "separator",
	"identifier": "identifier",
	"operator": "operator",
	"real": "real",
	"int": "int"
}

sym_regex = regex.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$")
real_regex = regex.compile(r"(?:[0-9]+\.[0-9]*)(?:[eE][-+]?[0-9]+)?$")
int_regex = regex.compile(r"[0-9]+$")
space_regex = regex.compile(r"(\r\n|\s|\n)+$")
many_ops_regex = regex.compile(r"(==|!=|<=|>=|<<<|>>>|<<|>>|\|=|&=|\^=|\+=|-=|\*=|\/=|%=)$")
sole_ops_regex = regex.compile(r"[=+\-*\/%&|<>!]$")

sep_regex = regex.compile(r"[;,\(\)\[\]\{\}]$")

first_sym_regex = regex.compile(r"[a-zA-Z_]")
first_num_regex = regex.compile(r"[0-9]")

class PeekableGenerator:
	def __init__(self, generator):
		self.generator = generator
		self.buffer = []
		self._fill_buffer()

	def _fill_buffer(self, count = 1):
		for _ in range(count):
			try:
				self.buffer.append(next(self.generator))
			except StopIteration:
				break

	def __iter__(self):
		return self

	def __next__(self):
		if not self.buffer:
			raise StopIteration
		res = self.buffer.pop(0)
		self._fill_buffer()
		return res

	def peek(self, pos = 0):
		if pos + 1 > len(self.buffer):
			self._fill_buffer(pos + 1 - len(self.buffer))
		try:
			return self.buffer[pos]
		except IndexError:
			return None

def file_char_stream(file_path):
	with open(file_path, "r") as file:
		while True:
			char = file.read(1)
			if not char:
				break
			yield char

def lexer_regex(partial_regex, peekable_char_stream, peek_only = False):
	matched = ""
	current_pos = 0
	peeked_char = None
	
	while peekable_char_stream.peek():
		peeked_char = peekable_char_stream.peek(current_pos if peek_only else 0)
		if peeked_char is None:
			break
		current_match = partial_regex.fullmatch(matched + peeked_char, partial=True)

		if current_match is None:
			break
		else:
			matched += peeked_char
			current_pos = len(matched)
			if not peek_only:
				next(peekable_char_stream)

	return (matched, "" if peeked_char is None else peeked_char)

def lexer(char_stream):
	res = []

	while True:
		char = char_stream.peek()

		if char is None:
			break
		elif regex.match(space_regex, char):
			lexer_regex(space_regex, char_stream)
		elif regex.match(first_sym_regex, char):
			temp_lexeme = lexer_regex(sym_regex, char_stream)[0]
			if temp_lexeme in keyword:
				res.append((temp_lexeme, token["keyword"]))
			else:
				res.append((temp_lexeme, token["identifier"]))
		elif regex.match(first_num_regex, char):
			temp_lexeme = lexer_regex(int_regex, char_stream, True)
			if temp_lexeme[1] == ".":
				res.append((lexer_regex(real_regex, char_stream)[0], token["real"]))
			else:
				res.append((temp_lexeme[0], token["int"]))
				for _ in range(len(temp_lexeme[0])):
					next(char_stream)
		elif regex.match(sep_regex, char):
			res.append((lexer_regex(sep_regex, char_stream)[0], token["separator"]))
		elif regex.match(sole_ops_regex, char):
			temp_lexeme = lexer_regex(many_ops_regex, char_stream, True)
			if len(temp_lexeme[0]) > 1:
				res.append((temp_lexeme[0], token["operator"]))
				for _ in range(len(temp_lexeme[0])):
					next(char_stream)
			else:
				res.append((lexer_regex(sole_ops_regex, char_stream)[0], token["operator"]))
		else:
			print("Invalid character: " + char)
			sys.exit(1)
	
	return res

lexer_res = lexer(PeekableGenerator(file_char_stream("input_scode.txt")))

print("token".ljust(12) + "| lexeme")
print("-" * 12 + "|" + "-" * 12)
for lexeme, token in lexer_res:
	print(token.ljust(12) + "| " + lexeme)

with open("output.txt", "w", newline='') as file:
	csv_writer(file).writerow(["token", "lexeme"])
	for lexeme, token in lexer_res:
		csv_writer(file).writerow([token, lexeme])