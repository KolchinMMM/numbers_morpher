import words2numsrus


extractor = words2numsrus.NumberExtractor()


def get_list_of_numerals(sentence):
    """Возвращает список словесных числительных в предложении"""
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
    """Ищет буквенные числительные в двух текстах и сравнивает их.
    Возвращает количество совпадений и общее количество числительных в 1 предложении"""
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


#
# with open("dir/other.json", encoding="utf-8") as file:
#     things = file.read()
# d = dict(json.loads(things))
#
# for sentence in d.keys():
#     print(sentence)
#     compare(sentence, "abc")