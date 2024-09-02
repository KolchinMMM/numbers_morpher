import os

main_file = open("main.txt", "w", encoding="utf-8")
for file in os.listdir("C:/Users/Михаил/Desktop/numbers_morpher/float_txt/"):
    with open(f"float_txt/{file}", "r", encoding="utf-8") as f:
        main_file.write(f.read())
main_file.close()