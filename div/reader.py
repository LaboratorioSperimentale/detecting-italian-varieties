import csv
import collections
import json

import pandas as pd

def read_metadata(kip_metadata_filename, kipasti_metadata_filename,
				  output_folder):

	NORD = ["emilia-romagna", "veneto", "lombardia", "piemonte", "valle-d-aosta",
		 "friuli-venezia-giulia", "liguria"]
	CENTRO = ["umbria", "toscana", "marche", "lazio"]
	SUD = ["campania", "abruzzo", "basilicata", "sardegna", "sicilia", "calabria"]
	ALTRO = ["estero"]

	participants = {}
	conversations = collections.defaultdict(lambda: {"participants": [], "setting": None, "area": None, "age_group": None})


	with open(kip_metadata_filename) as fin:
		reader = csv.reader(fin, delimiter=',')
		header = reader.__next__()
		# print(header)
		for line in reader:
			participants[line[0]] = {"code": line[0],
									"occupation": line[1],
									"age": [int(x) for x in line[5].split("-")],
									"region": line[4]}
			convs = line[3].strip().split(",")
			for c in convs:
				conversations[c.strip()]["participants"].append(line[0])
				conversations[c.strip()]["setting"] = "interview"
			# print(conversations)
			# input()

	with open(kipasti_metadata_filename) as fin:
		reader = csv.reader(fin, delimiter=',')
		header = reader.__next__()
		# print(header)
		for line in reader:
			participants[line[0]] = {"code": line[0],
									"occupation": line[1],
									"age": [int(x) for x in line[5].split("-")],
									"region": line[4]}
			convs = line[3].strip().split(",")
			for c in convs:
				conversations[c.strip()]["participants"].append(line[0])
				conversations[c.strip()]["setting"] = "dinnertable"
			# print(conversations)
			# input()

	for conv in conversations:
		# print(conv, len(conversations[conv]["participants"]))
		conv_participants = [participants[x] for x in conversations[conv]["participants"]]

		part_in_NORD = [x["region"] in NORD for x in conv_participants]
		part_in_SUD = [x["region"] in SUD for x in conv_participants]
		part_in_CENTRO = [x["region"] in CENTRO for x in conv_participants]

		part_giovani = [x["age"][1]<41 for x in conv_participants]
		part_adulti = [x["age"][0]>40 for x in conv_participants]

		if all(part_in_NORD) or all(part_in_SUD) or all(part_in_CENTRO):
			conversations[conv]["area"] = "homogeneous"
		else:
			conversations[conv]["area"] = "non-homogeneous"

		if all(part_giovani) or all(part_adulti):
			conversations[conv]["age_group"] = "homogeneous"
		else:
			conversations[conv]["age_group"] = "non-homogeneous"

		# print(len(conversations[conv]["partecipanti"]))
		# print([participants[x] for x in conversations[conv]["partecipanti"]])
		# input(conversations[conv])
		# print(conv_participants)
		# input()


	with open(f"{output_folder}/participants.json", "w") as fout:
		print(json.dumps(participants, indent=4), file=fout)
	with open(f"{output_folder}/conversations.json", "w") as fout:
		print(json.dumps(conversations, indent=4), file=fout)


# manual_features, automatic_features, semiautomatic_features,
# 					participants_metadata, conversations_metadata,
# 					args.output_folder

def read_traits(input_filenames_manuali,
				input_filenames_automatici,
				input_filenames_semiautomatici,
				participants_metadata, conversations_metadata,
				output_folder):

	data = collections.defaultdict(lambda: collections.defaultdict(int))


	for filename in input_filenames_manuali:
		with open(filename, encoding="utf-8") as fin:
			reader = csv.reader(fin, delimiter=',')
			header = reader.__next__()
			print(header)
			for line in reader:
				conv_id = line[1].strip()

				conv_area = conversations_metadata[conv_id]["area"]
				conv_age = conversations_metadata[conv_id]["age_group"]

				speaker_id = line[3].strip()

				tratti = ["Verbi sintagmatici", "V intrans uso trans", "Oggetto preposiz.", "Che interrogative disgiuntive", "La Nproprio", "Sovraest. a vocale tematica", "Prep. da per di", "Lo/la/le/li ne", "Malapropismi", "Desinenze nominali analogiche", "Accordo semantico relativa S", "V sg. + Sogg. pl.", "Scambi di ausiliari", "Elementi in inglese (ev. CS)", "Elementi in dialetto (ev. CS)", "Altre lingue (extra-repertorio)"]

				tratti_valori = [int(x) for x in line[5:5+len(tratti)]]

				tratti = dict(zip(tratti, tratti_valori))

				for tratto, valore in tratti.items():
					if valore > 0:
						data[(speaker_id, conv_area, conv_age)][tratto] += valore
		print(data)
		input()

	for filename in input_filenames_automatici:
		feat_name = filename.stem
		# print(feat_name)
		df = pd.read_excel(filename)
		for index, row in df.iterrows():
			data[row["SPEAKER"]]["features"][feat_name] += 1
			# print(row["SPEAKER"])
			# input()

	for speaker in data:
		if len(data[speaker]["features"]) > 0:
			print(json.dumps(data[speaker], indent=4),
		 		file=open(output_folder.joinpath(f"{speaker}.json"), "w"))


if __name__ == "__main__":
	import pathlib
	read_traits([pathlib.Path("/home/ludop/Documents/iclave-12/data/annotazioni/tratti.csv")],
			  [pathlib.Path("/home/ludop/Documents/iclave-12/data/annotazioni/simple/PATTERN_questoqui_quellili.xlsx")],
			  [pathlib.Path("/home/ludop/Documents/iclave-12/data/annotazioni/annotated/LEMMA_cacciare.xlsx")],
			  pathlib.Path("/home/ludop/Documents/iclave-12/data/annotazioni/KIP_participants.csv"),
			  pathlib.Path("/home/ludop/Documents/iclave-12/data/annotazioni/KIPasti_participants.csv"),
			  pathlib.Path("../output_feats/"))