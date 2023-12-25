from stanza_json import process_num, contains_num
from process_word import switch_case
import stanza
import json


nlp = stanza.Pipeline('ru', download_method=False, warnings=False)

with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))

# texts = [
#     "Игра стала полностью трёхмерной, с видом от 3 лица.",
#     "Небольшая часть территории была присоединена 11 Инкой — Уайна Капаком",
#     "Он создал настоящую империю, ведь до этого инки были всего лишь 1 из многочисленных индейских племен, а Куско — обычным городком. advcl",
#     "Эта война завершила серию колониальных войн между Англией и Францией, которые иногда называют 2 Столетней войной",
#     "При короле Георге II в колониях случились 2 войны с интервалом в несколько лет; из них войной короля Георга называют только 1 obl",
#     "По разным данным, жертвами удара стали по несколько военнослужащих и мирных жителей, ранения получили около 2 с половиной десятков человек.",
#     "Кукла «Кандидат околовсяческих наук Венера Михайловна Пустомельская» существует как минимум в 2 экземплярах",
#     "Следует отметить, что в зависимости от вашего желания можно не использовать параметры, умения или таланты, а также использовать что-то 1 или вообще назвать это по-другому.",
# ]
#
# d = {}
# for t in texts:
#     d[t] = t


file_wrong = open("wrong.txt", "w", encoding="utf-8")
file_right = open("right.txt", "w", encoding="utf-8")

count = 0
count_correct = 0
for correct, s in d.items():
    count += 1
    print(count)
    if count >= 500:
        break
    nlpied = nlp(s)
    for sentence in nlpied.sentences:
        new_sentence = sentence.text
        print(new_sentence)
        for word in sentence.words:
            if (word.upos == "NUM" or word.upos == "ADJ") and contains_num(word.text):
                struct = process_num(word, sentence, word.deprel, word.text)
                print(struct)
                new_word = switch_case(word.text, struct["case"], struct["gender"], struct["number"], struct["type"])
                new_sentence = new_sentence.replace(word.text, new_word.strip())
        print(new_sentence)
        if new_sentence.lower() == correct.lower():
            count_correct += 1
        else:
            file_right.write(s+"\n")
            file_wrong.write(new_sentence+"\n")


file_wrong.close()
print(f"Acc: {count_correct/count} {count_correct}/{count}")




