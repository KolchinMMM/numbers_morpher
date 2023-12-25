from process_word import switch_case
import re
import json

print(switch_case(3, "Nom", "Masc", "Sing", "NUM"))

print(switch_case(1000, "Gen", "Masc", "Plur", "NUM"))


# Animacy=Inan|Case=Acc|Gender=Fem|Number=Sing"