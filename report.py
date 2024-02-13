import json

with open("dir/1.json", encoding="utf-8") as file:
    things = file.read()

d = dict(json.loads(things))


for i in d.values():
    print(i)
exit()

x = str(input("""Метод ввода теста:
1.) Вручную
2.) Файл
Ввод: """))


xx = str(input("Введите текст:\n"))

print("Измененное предложение:\nЗдесь произошло столкновение, известное как Сражение у тысячи островов.")
