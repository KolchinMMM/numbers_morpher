from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json

nlp = stanza.Pipeline('ru', download_method=False, warnings=False)