import argparse
import pathlib
from pathlib import Path

import tqdm
import json
import pandas as pd

import yaml
try:
	from yaml import CLoader as Loader
except ImportError:
	from yaml import Loader

from div.utils import data_reader as du
from div import extractor
from div import reader


def _parse_data(args):
	"""
	The function `_parse_data` takes input directory path as argument, lists all `.txt` files in the
	directory, and then passes the list of files to `du.parse_data` along with the output directory
	path.

	Args:
	  args: the `args` parameter contains the `input_dir` and `output_dir` paths.
	"""

	input_dir = Path(args.input_dir)
	input_files = list(input_dir.glob("*.txt"))

	du.parse_data(input_files, args.output_dir)


def _extract_feats(args):
	"""
	The function `_extract_feats` extracts features from input files based on specified criteria and
	saves the results in TSV and Excel formats.

	Args:
	  args: The `_extract_feats` function takes in a dictionary `args` as a parameter.
	  The function reads this information from a YAML file specified in `args.features`.
	"""

	dictionary = yaml.load(open(args.features, encoding="utf-8"), Loader)
	input_folder_KIP = Path(dictionary["input_folder"]["KIP"])
	input_folder_KIPasti = Path(dictionary["input_folder"]["KIPasti"])

	output_folder = Path(dictionary["output_folder"])

	tratti = dictionary["tratti"]

	for tratto in tqdm.tqdm(tratti):
		name = tratto["name"]
		trait_type = tratto["type"]

		if trait_type == "VOC":
			files_list = [input_folder_KIP.joinpath(f"{x}.txt")
						  for x in dictionary["selected_conversations"]["KIP"]] + \
							[input_folder_KIPasti.joinpath(f"{x}.txt")
							 for x in dictionary["selected_conversations"]["KIPasti"]]
			ret = extractor.extract_voc(files_list, tratto["accepted_elements"])

		elif trait_type == "PATTERN":
			files_list = [input_folder_KIP.joinpath(f"{x}.txt")
						  for x in dictionary["selected_conversations"]["KIP"]] + \
							[input_folder_KIPasti.joinpath(f"{x}.txt")
							 for x in dictionary["selected_conversations"]["KIPasti"]]
			ret = extractor.extract_pattern(files_list,
											tratto["accepted_elements"], tratto["filter_elements"])

		elif trait_type == "LEMMA":
			files_list = [input_folder_KIP.joinpath(f"{x}.conllu")
						  for x in dictionary["selected_conversations"]["KIP"]] + \
							[input_folder_KIPasti.joinpath(f"{x}.conllu")
							 for x in dictionary["selected_conversations"]["KIPasti"]]
			ret = extractor.extract_lemma(files_list, tratto["accepted_elements"])

		elif trait_type == "MORPH":
			files_list = [input_folder_KIP.joinpath(f"{x}.conllu")
						  for x in dictionary["selected_conversations"]["KIP"]] + \
							[input_folder_KIPasti.joinpath(f"{x}.conllu")
							 for x in dictionary["selected_conversations"]["KIPasti"]]
			ret = extractor.extract_morph(files_list,
										  tratto["accepted_elements"], tratto["morph_features"])

		sorted_ret = list(sorted(ret, key=lambda x: (x[3], x[4])))
		with open(output_folder.joinpath(f"{tratto['type']}_{tratto['name']}.tsv"), "w",
				  encoding="utf-8") as fout:
			print("CONV\tSPEAKER\tPRE_CTX\tHIT\tPOST_CTX", file=fout)
			for r in sorted_ret:
				print("\t".join(r), file=fout)

		df1 = pd.DataFrame(sorted_ret, columns=["CONV", "SPEAKER", "PRE_CTX", "HIT", "POST_CTX"])
		df1.to_excel(output_folder.joinpath(f"{tratto['type']}_{tratto['name']}.xlsx"))

		print(f"Extracting trait: {name}, writing output to {tratto['type']}_{tratto['name']}")


def _parse_metadata(args):

	kip_files = args.kip_folder.glob("*.conllu")
	kipasti_files = args.kipasti_folder.glob("*.conllu")

	reader.read_metadata(args.kip_metadata, args.kipasti_metadata,
					  kip_files, kipasti_files,
					  args.output_folder)


def _read_traits(args):

	manual_features = list(args.manual_features_dir.glob("*.csv"))
	automatic_features = list(args.automatic_features_dir.glob("*.xlsx"))
	semiautomatic_features = list(args.semiautomatic_features_dir.glob("*.xlsx"))

	participants_metadata = json.load(open(args.participants_metadata_fname))
	conversations_metadata = json.load(open(args.conversations_metadata_fname))

	print(participants_metadata)
	print(conversations_metadata)
	# print(semiautomatic_features)

	reader.read_traits(manual_features, automatic_features, semiautomatic_features,
					participants_metadata, conversations_metadata,
					args.output_folder)


if __name__ == "__main__":

	parent_parser = argparse.ArgumentParser(add_help=False)

	root_parser = argparse.ArgumentParser(prog='div', add_help=True)
	subparsers = root_parser.add_subparsers(title="actions", dest="actions")

	parser_processdata = subparsers.add_parser('process', parents=[parent_parser],
											   description='run NLP Pipeline',
											   help='run NLP Pipeline')
	parser_processdata.add_argument("-o", "--output-dir", default="data/parsed/",
								   help="path to output dir, default is data/parsed/")
	parser_processdata.add_argument("-i", "--input-dir",
									help="path to folder containing corpus in .txt format")
	parser_processdata.set_defaults(func=_parse_data)



	parser_extractfeatures = subparsers.add_parser('extract', parents=[parent_parser],
													description='extract features',
													help='extract featurses')
	parser_extractfeatures.add_argument("-o", "--output-dir", default="data/contexts/",
										help="path to output dir, default is data/contexts/")
	parser_extractfeatures.add_argument("-f", "--features", required=True,
										help="path to features cfg file")
	parser_extractfeatures.set_defaults(func=_extract_feats)


	parser_conversations = subparsers.add_parser("conversation-metadata", parents=[parent_parser],
											description="extract conversation metadata",
											help="extract conversation metadata")
	parser_conversations.add_argument("--kip-metadata", type=pathlib.Path)
	parser_conversations.add_argument("--kipasti-metadata",type=pathlib.Path)
	parser_conversations.add_argument("--kip-folder", type=pathlib.Path)
	parser_conversations.add_argument("--kipasti-folder", type=pathlib.Path)
	parser_conversations.add_argument("-o", "--output-folder", type=pathlib.Path)
	parser_conversations.set_defaults(func=_parse_metadata)


	parser_aggregatefeats = subparsers.add_parser("aggregate", parents=[parent_parser],
												  description="aggregate features for participant",
												  help="aggregate features for participant")
	parser_aggregatefeats.add_argument("-o", "--output-folder", type=pathlib.Path)
	parser_aggregatefeats.add_argument("--participants-metadata-fname", type=pathlib.Path)
	parser_aggregatefeats.add_argument("--conversations-metadata-fname", type=pathlib.Path)
	parser_aggregatefeats.add_argument("--manual-features-dir", type=pathlib.Path)
	parser_aggregatefeats.add_argument("--automatic-features-dir", type=pathlib.Path)
	parser_aggregatefeats.add_argument("--semiautomatic-features-dir", type=pathlib.Path)
	parser_aggregatefeats.set_defaults(func=_read_traits)


	args = root_parser.parse_args()

	if "func" not in args:
		root_parser.print_usage()
		exit()

	args.func(args)
