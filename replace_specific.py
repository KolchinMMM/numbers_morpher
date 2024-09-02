import stanza
import re
from process_word import switch_case


nlp = stanza.Pipeline("ru")

texts = ["около 2-3 человек", "вот так (1234-4355)"]

for text in texts:
    for sentence in nlp(text).sentences:
        new_sentence = sentence.text
        years = re.findall("[(][0-9]+[—–−-][0-9]+[)]", text)
        if years:
            for year in years:
                year = year[1:-1]
                for word in re.split("[—–−-]", year):
                    a = switch_case(word, "Nom", "masc", "sing", "ADJ")
                    print(a)
                    print(word)
                    new_sentence = new_sentence.replace(word, a)
        print(new_sentence)
