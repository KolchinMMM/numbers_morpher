import stanza
import re
import deplacy



def contains_num(s):
    return any(i.isdigit() for i in s)


nlp = stanza.Pipeline('ru', download_method=False)
filename = "specific.txt"

with open(filename, "r", encoding="utf-8") as file:
    texts = file.read().split("\n")
# texts = ["Кроме того, он видел по ее приемам, что она 1 из тех женщин, особенно матерей, которые, однажды взяв себе что-нибудь в голову, не отстанут до тех пор, пока не исполнят их желания, "
#          "а в противном случае готовы на ежедневные, ежеминутные приставания и даже на сцены.Теперь я знаю, что не для нее 1, не для себя 1, но и для всех это должно неизбежно свершиться."
#          "Она, как и всегда, с простотой своей отвечала, что нынешние именины были для нее 1 из самых приятных.Пьеру, напротив, казалось, что это место (именно потому, что он находился на нем) было 1 из самых незначительных мест сражения."
#          "Римский понял, что он давно 1 во всем 2 этаже, и детский неодолимый страх овладел им при этой мысли."]

for se in texts:
    d = nlp(se)
    deplacy.render(d)
    for s in d.sentences:
        for t in s.words:
            if contains_num(t.text):
                print("\n@@@@@@")
            print(t)
            if contains_num(t.text):
                print("@@@@@@\n")
