from pathlib import Path
from typing import List

import regex as re

from div.utils import data_reader as du


def extract_voc(files_list: List[Path], voc_list: List[str],
				context_width: int = 200):
	"""
	This Python function extracts occurrences of specified vocabulary words within a given context width
	from a list of files.

	Args:
	  files_list (List[Path]): The `files_list` parameter is a list of file paths that the function will
	process to extract vocabulary occurrences.
	  voc_list (List[str]): The `voc_list` parameter is a list of strings that contains the vocabulary
	terms you want to extract from the conversations. These terms will be used to search for occurrences
	within the conversation turns.
	  context_width (int): The `context_width` parameter in the `extract_voc` function determines the
	number of characters to include before and after the occurrence of a vocabulary item in the text.
	This context is extracted to provide additional context around the vocabulary item for analysis or
	processing. Defaults to 200

	Returns:
	  The function `extract_voc` returns a list of tuples, where each tuple contains the conversation,
	speaker, previous context, context (containing the vocabulary word), and next context for
	occurrences of vocabulary words in the input files.
	"""

	ret = []

	for file in files_list:
		turns = du.create_turns(file)
		for turn in turns:
			conv, speaker, turn = turn
			conflated_turn = " "
			for subturn in turn:
				for x in subturn:
					conflated_turn+=f"{x} "

			for element in voc_list:
				pattern = re.compile(r" {} ".format(element))

				occs = [m.start() for m in re.finditer(pattern, conflated_turn, overlapped=True)]

				if len(occs)>0:
					for occ in occs:
						prev_ctx = conflated_turn[max(0, occ-context_width):occ]
						ctx = conflated_turn[occ:occ+len(element)+1]
						next_ctx = conflated_turn[occ+len(element)+1:min(len(conflated_turn),
													   occ+len(element)+1+context_width)]

						ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret


def extract_pattern(files_list: List[Path], voc_list: List[str],
					voc_to_filter: List[str],
					context_width: int = 200):
	"""
	The function `extract_pattern` takes a list of files, vocabulary list, vocabulary to filter, and
	context width as input, extracts patterns from the files based on the vocabulary list, and returns
	the context surrounding the patterns that are not in the filter list.

	Args:
	  files_list (List[Path]): The `files_list` parameter is a list of file paths that contain the data
	you want to extract patterns from.
	  voc_list (List[str]): The `voc_list` parameter is a list of strings that contains the vocabulary
	terms you want to extract patterns for in the text data. These terms will be used to create regular
	expressions for pattern matching in the text.
	  voc_to_filter (List[str]): The `voc_to_filter` parameter is a list of strings that are used to
	filter out specific occurrences of the pattern found in the text. If the context containing the
	pattern matches any of the strings in `voc_to_filter`, then that particular occurrence will not be
	included in the final result.
	  context_width (int): The `context_width` parameter in the `extract_pattern` function determines
	the number of characters to include before and after the matched pattern in the context. It
	specifies the width of the context window around the matched pattern within the `conflated_turn`
	string. Defaults to 200

	Returns:
	  The function `extract_pattern` returns a list of tuples containing contextual information related
	to occurrences of vocabulary words in the input files. Each tuple includes the conversation ID,
	speaker, previous context, matched vocabulary word, and next context for each occurrence found in
	the input files.
	"""

	ret = []

	for file in files_list:
		turns = du.create_turns(file)
		for turn in turns:
			conv, speaker, turn = turn
			conflated_turn = " "
			for subturn in turn:
				for x in subturn:
					conflated_turn+=f"{x} "

			for element in voc_list:
				pattern = re.compile(r"{} ".format(element))

				occs = [m.span() for m in re.finditer(pattern, conflated_turn, overlapped=True)]

				if len(occs)>0:

					for occ in occs:
						occ_start, occ_end = occ

						prev_ctx = conflated_turn[max(0, occ_start-context_width):occ_start]
						ctx = conflated_turn[occ_start:occ_end]
						next_ctx = conflated_turn[occ_end:min(len(conflated_turn), occ_end+context_width)]

						if not ctx.strip() in voc_to_filter:
							ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret


def extract_lemma(files_list: List[Path], voc_list: List[str],
				  context_width: int = 200):
	"""
	This function extracts lemmas and their surrounding contexts from a list of files based on a
	vocabulary list.

	Args:
	  files_list (List[Path]): The `files_list` parameter is a list of file paths that contain data to
	be processed.
	  voc_list (List[str]): The `voc_list` parameter in the `extract_lemma` function is a list of
	strings. Each string in this list represents a lemma that you want to search for in the text data.
	The function will look for occurrences of these lemmas in the text data and extract contextual
	information around each
	  context_width (int): The `context_width` parameter in the `extract_lemma` function determines the
	number of character to include before and after the target word (specified in `voc_list`) in the
	context. This parameter controls the size of the context window around the target word for
	extracting information. Defaults to 200

	Returns:
	  The function `extract_lemma` returns a list of tuples, where each tuple contains the following
	elements:
	1. Conversation ID (`conv`)
	2. Speaker ID (`speaker`)
	3. Previous context words before the occurrence of the vocabulary word (`prev_ctx`)
	4. Vocabulary word itself (`ctx`)
	5. Next context words after the occurrence of the vocabulary word (`next_ctx`)
	"""


	ret = []

	for file in files_list:
		turns = du.create_turns_conll(file)

		for turn in turns:
			conv, speaker, turn = turn
			conflated_turn = " "
			for subturn in turn:
				for form, lemma, pos, _ in subturn:
					conflated_turn+=f"{form}/{lemma}/{pos} "

			for element in voc_list:

				pattern = re.compile(r" {} ".format(element))
				occs = [m.span() for m in re.finditer(pattern, conflated_turn, overlapped=True)]

				if len(occs)>0:
					for occ in occs:
						occ_start, occ_end = occ

						prev_ctx = conflated_turn[max(0, occ_start-context_width):occ_start]
						ctx = conflated_turn[occ_start:occ_end]
						next_ctx = conflated_turn[occ_end:min(len(conflated_turn),
											occ_end+context_width)]

						prev_ctx = prev_ctx.split(" ")
						prev_ctx = [x.split("/")[0] for x in prev_ctx]
						prev_ctx = " ".join(prev_ctx)

						ctx = ctx.split(" ")
						ctx = [x.split("/")[0] for x in ctx]
						ctx = " ".join(ctx)

						next_ctx = next_ctx.split(" ")
						next_ctx = [x.split("/")[0] for x in next_ctx]
						next_ctx = " ".join(next_ctx)

						ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret


def extract_morph(files_list: List[Path], voc_list: List[str],
				  morph_feats: List[str], context_width: int = 200):
	"""
	The function `extract_morph` takes a list of files, a list of vocabulary items, a list of
	morphological features, and a context width, and extracts contextual information around occurrences
	of vocabulary items with specified morphological features in the files.

	Args:
	  files_list (List[Path]): The `files_list` parameter is a list of file paths that the function will
	iterate over to extract morphological features from.
	  voc_list (List[str]): The `voc_list` parameter in the `extract_morph` function is a list of
	strings that represent vocabulary items you want to search for within the `conflated_turn` text.
	These strings will be used as patterns to find occurrences within the text and extract context
	around them.
	  morph_feats (List[str]): The `morph_feats` parameter in the `extract_morph` function is a list of
	morphological features that you want to extract from the input data. These features could include
	attributes such as tense, number, gender, case, etc., which provide information about the
	grammatical properties of a word.
	  context_width (int): The `context_width` parameter in the `extract_morph` function determines the
	number of characters to include in the context before and after the target word when extracting
	linguistic features.

	Returns:
	  The function `extract_morph` returns a list of tuples, where each tuple contains the following
	elements:
	1. Conversation ID (`conv`)
	2. Speaker ID (`speaker`)
	3. Previous context words before the occurrence of a vocabulary item (`prev_ctx`)
	4. Vocabulary item itself (`ctx`)
	5. Next context words after the occurrence of the vocabulary item (`next_ctx`)
	"""

	ret = []

	for file in files_list:
		turns = du.create_turns_conll(file)

		for turn in turns:
			conv, speaker, turn = turn
			conflated_turn = " "
			for subturn in turn:
				for form, lemma, pos, morph in subturn:
					w = f"{form}/{lemma}/{pos}"
					for feat in morph_feats:
						w += f"/{feat}={morph[feat]}"
					conflated_turn+=f"{w} "

			for element in voc_list:

				pattern = re.compile(r" {} ".format(element))
				occs = [m.span() for m in re.finditer(pattern, conflated_turn, overlapped=True)]

				if len(occs)>0:
					for occ in occs:
						occ_start, occ_end = occ

						prev_ctx = conflated_turn[max(0, occ_start-context_width):occ_start]
						ctx = conflated_turn[occ_start:occ_end]
						next_ctx = conflated_turn[occ_end:min(len(conflated_turn), occ_end+context_width)]

						prev_ctx = prev_ctx.split(" ")
						prev_ctx = [x.split("/")[0] for x in prev_ctx]
						prev_ctx = " ".join(prev_ctx)

						ctx = ctx.split(" ")
						ctx = [x.split("/")[0] for x in ctx]
						ctx = " ".join(ctx)

						next_ctx = next_ctx.split(" ")
						next_ctx = [x.split("/")[0] for x in next_ctx]
						next_ctx = " ".join(next_ctx)

						ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret
