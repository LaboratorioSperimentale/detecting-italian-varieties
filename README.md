# ICLAVE-12 and ICL submission

* Traits are described in file `TRATTI.md` and defined in `traits.yaml`

* In order to extract traits CoNLL-formatted files are needed, an example can be seen below:
```
# speaker = PKP025
# conversation = KPC001
# sent_id = 1
# text = faccio il tè
0	faccio	fare	VERB	V	ROOT	0	Mood=Ind|Number=Sing|Person=1|Tense=Pres|VerbForm=Fin
1	il	il	DET	RD	det	2	Definite=Def|Gender=Masc|Number=Sing|PronType=Art
2	tè	tè	NOUN	S	obj	0	Gender=Masc

# speaker = PKP026
# conversation = KPC001
# sent_id = 1
# text = allora
0	allora	allora	ADV	B	ROOT	0
```

* In order to run the extraction process, execute:
```
python main.py extract -f traits.yaml
```