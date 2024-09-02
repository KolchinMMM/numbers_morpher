import stanza
import words2numsrus
import json
# nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

extractor = words2numsrus.NumberExtractor()
# for match in extractor(sentence1):
#     print(match)
#
# for word in sentence1.split():
#     print(word)
#     print(extractor(word).matches)


def get_list_of_numerals(sentence):
    tokenized = []
    current_token = ""
    flag_numeral_currently = False
    for word in sentence.split():
        if extractor(word).matches != [] or (word[:3].lower() == "цел" and flag_numeral_currently):
            if not flag_numeral_currently:
                flag_numeral_currently = True
            current_token += word
        else:
            if flag_numeral_currently:
                tokenized.append(current_token)
                current_token = ""
                flag_numeral_currently = False
    if current_token != "":
        tokenized.append(current_token)
    return tokenized


def compare(sentence1, sentence2):
    tokenized1 = get_list_of_numerals(sentence1)
    tokenized2 = get_list_of_numerals(sentence2)
    last_found_index = -1
    count_all = 0
    count_right = 0
    for token_orig in tokenized1:
        for i in range(last_found_index + 1, len(tokenized2)):
            if token_orig.lower().strip() == tokenized2[i].lower().strip():
                count_right += 1
                continue
        count_all += 1
    return count_right, count_all



a = "пять целых три сотых людей"
b = "пять целых три десятых людей"
print(compare(a, b))

#
# with open("dir/other.json", encoding="utf-8") as file:
#     things = file.read()
# d = dict(json.loads(things))
#
# for sentence in d.keys():
#     print(sentence)
#     compare(sentence, "abc")