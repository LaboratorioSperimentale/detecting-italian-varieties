import re

from pathlib import Path
from typing import List

from div.utils import data_reader as du

def extract_voc(voc_list: List[str], 
				context_width: int = 200) -> None:
	files_list = list(Path("data/KIPasti_txt").glob("*.txt"))

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

				occs = [m.start() for m in re.finditer(pattern, conflated_turn)]
				if len(occs)>0:
					
					for occ in occs:
						prev_ctx = conflated_turn[max(0, occ-context_width):occ]
						ctx = conflated_turn[occ:occ+len(element)+1]
						next_ctx = conflated_turn[occ+len(element)+1:min(len(conflated_turn), occ+len(element)+1+context_width)]

						print(element)
						print(conflated_turn)
						print("PREV", prev_ctx)
						print(ctx)
						print("NEXT", next_ctx)
						input()