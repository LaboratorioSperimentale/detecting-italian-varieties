import argparse
from pathlib import Path

import pandas as pd

import yaml

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import div
from div.utils import data_reader as du
from div import extractor


def _parse_data(args):

    input_dir = Path(args.input_dir)
    input_files = list(input_dir.glob("*.txt"))

    du.parse_data(input_files, args.output_dir)


def _extract_feats(args):


    dictionary = yaml.load(open(args.features), Loader)
    input_folder_KIP = Path(dictionary["input_folder"]["KIP"])
    input_folder_KIPasti = Path(dictionary["input_folder"]["KIPasti"])

    output_folder = Path(dictionary["output_folder"])

    tratti = dictionary["tratti"]

    for tratto in tratti:
        name = None
        type = tratto["type"]

        if type == "VOC":
            files_list = [input_folder_KIP.joinpath(f"{x}.txt") for x in dictionary["selected_conversations"]["KIP"]] + [input_folder_KIPasti.joinpath(f"{x}.txt") for x in dictionary["selected_conversations"]["KIPasti"]]
            ret = extractor.extract_voc(files_list, tratto["accepted_elements"])

        elif type == "PATTERN":
            files_list = [input_folder_KIP.joinpath(f"{x}.txt") for x in dictionary["selected_conversations"]["KIP"]] + [input_folder_KIPasti.joinpath(f"{x}.txt") for x in dictionary["selected_conversations"]["KIPasti"]]
            ret = extractor.extract_pattern(files_list, tratto["accepted_elements"],
                                            tratto["filter_elements"])

        elif type == "LEMMA":
            files_list = [input_folder_KIP.joinpath(f"{x}.conllu") for x in dictionary["selected_conversations"]["KIP"]] + [input_folder_KIPasti.joinpath(f"{x}.conllu") for x in dictionary["selected_conversations"]["KIPasti"]]
            ret = extractor.extract_lemma(files_list, tratto["accepted_elements"])




        sorted_ret = list(sorted(ret, key=lambda x: x[3]))
        with open(output_folder.joinpath(f"{tratto['type']}_{tratto['name']}.tsv"), "w") as fout:
            print("CONV\tSPEAKER\tPRE_CTX\tHIT\tPOST_CTX", file=fout)
            for r in sorted_ret:
                print("\t".join(r), file=fout)



        df1 = pd.DataFrame(sorted_ret, columns=["CONV", "SPEAKER", "PRE_CTX", "HIT", "POST_CTX"])
        df1.to_excel(output_folder.joinpath(f"{tratto['type']}_{tratto['name']}.xlsx"))

if __name__ == "__main__":

    parent_parser = argparse.ArgumentParser(add_help=False)

    root_parser = argparse.ArgumentParser(prog='div', add_help=True)
    # root_parser.set_defaults(func=)
    subparsers = root_parser.add_subparsers(title="actions", dest="actions")


    parser_processdata = subparsers.add_parser('process', parents=[parent_parser],
                                               description='run NLP Pipeline',
                                               help='run NLP Pipeline')
    parser_processdata.add_argument("-o", "--output-dir", default="data/parsed/",
                                   help="path to output dir, default is data/parsed/")
    parser_processdata.add_argument("-i", "--input-dir", help="path to folder containing corpus in .txt format")
    # parser_processdata.add_argument("--model", help="name of spacy model", default="it_core_news_lg")
    # parser_processdata.add_argument("--type", default="KIP", choices=["KIP", "KIPasti"])
    parser_processdata.set_defaults(func=_parse_data)


    parser_extractfeatures = subparsers.add_parser('extract', parents=[parent_parser],
                                                    description='extract features',
                                                    help='extract features')
    parser_extractfeatures.add_argument("-o", "--output-dir", default="data/contexts/",
                                        help="path to output dir, default is data/contexts/")
    parser_extractfeatures.add_argument("-f", "--features", required=True,
                                        help="path to features cfg file")
    parser_extractfeatures.set_defaults(func=_extract_feats)


    args = root_parser.parse_args()

    if "func" not in args:
        root_parser.print_usage()
        exit()

    args.func(args)