import csv
import razdel
import time


def has_number(text):
    for char in text:
        if char.isdigit():
            return True
    return False


def main():
    time_start = time.perf_counter()
    file_to_open_path = "news.csv"
    file_to_write = "file_short.txt"
    writer = open(file_to_write, "w", encoding="utf-8", newline="")

    with open(file_to_open_path, "r", encoding="utf-8") as file_read:
        count = 0
        csvreader = csv.reader(file_read)
        for row in csvreader:
            sentences = razdel.sentenize(row[2])
            for sentence in sentences:
                if has_number(sentence.text) and len(sentence.text)<128:
                    count += 1
                    writer.write(f"{sentence.text}\n")
    time_end = time.perf_counter()
    print(f"Done! Count: {count}, spent time: {time_end - time_start}")


if __name__ == "__main__":
    main()
