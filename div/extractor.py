# import re
import regex as re

from pathlib import Path
from typing import List

from div.utils import data_reader as du

def extract_voc(files_list: List[Path], voc_list: List[str],
				context_width: int = 200):

	ret = []

	for file in files_list:
		turns = du.create_turns(file)
		for turn in turns:
			conv, speaker, turn = turn
			conflated_turn = " "
			for subturn in turn:
				for x in subturn:
					conflated_turn+=f"{x} "


			# print(conflated_turn, len(conflated_turn))
			for element in voc_list:
				pattern = re.compile(r" {} ".format(element))

				occs = [m.start() for m in re.finditer(pattern, conflated_turn, overlapped=True)]


				if len(occs)>0:
					# print(occs)
					# input()
					for occ in occs:
						prev_ctx = conflated_turn[max(0, occ-context_width):occ]
						ctx = conflated_turn[occ:occ+len(element)+1]
						next_ctx = conflated_turn[occ+len(element)+1:min(len(conflated_turn), occ+len(element)+1+context_width)]

						ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret


def extract_pattern(files_list: List[Path], voc_list: List[str],
					voc_to_filter: List[str],
					context_width: int = 200):

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
						occ_len = occ_end - occ_start

						prev_ctx = conflated_turn[max(0, occ_start-context_width):occ_start]
						ctx = conflated_turn[occ_start:occ_end]
						next_ctx = conflated_turn[occ_end:min(len(conflated_turn), occ_end+context_width)]

						# prev_ctx = prev_ctx.split(" ")
						# prev_ctx = [x.split("/")[0] for x in prev_ctx]
						# prev_ctx = " ".join(prev_ctx)

						# ctx = ctx.split(" ")
						# ctx = [x.split("/")[0] for x in ctx]
						# ctx = " ".join(ctx)

						# next_ctx = next_ctx.split(" ")
						# next_ctx = [x.split("/")[0] for x in next_ctx]
						# next_ctx = " ".join(next_ctx)


						# prev_ctx = conflated_turn[max(0, occ-context_width):occ].split(" ")
						# ctx = prev_ctx[-1]+conflated_turn[occ:occ+len(element)+1]
						# next_ctx = conflated_turn[occ+len(element)+1:min(len(conflated_turn), occ+len(element)+1+context_width)]

						# if len(prev_ctx[-1])>1 and not prev_ctx[-1] in voc_to_filter:
						if not ctx.strip() in voc_to_filter:
							ret.append((conv, speaker, prev_ctx, ctx, next_ctx))

	return ret


def extract_lemma(files_list: List[Path], voc_list: List[str],
				  context_width: int = 200):

	ret = []

	for file in files_list:
		turns = du.create_turns_conll(file)

		for turn in turns:
			conv, speaker, turn = turn
			# print(conv, speaker, turn)
			# input()
			conflated_turn = " "
			for subturn in turn:
				for form, lemma, pos in subturn:
					conflated_turn+=f"{form}/{lemma}/{pos} "


			# print(conflated_turn, len(conflated_turn))
			# input()

			for element in voc_list:

				pattern = re.compile(r" {} ".format(element))

				occs = [m.span() for m in re.finditer(pattern, conflated_turn, overlapped=True)]

				if len(occs)>0:
					# print(element)
					# print(occs)
					# input()

					for occ in occs:
						occ_start, occ_end = occ
						occ_len = occ_end - occ_start

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