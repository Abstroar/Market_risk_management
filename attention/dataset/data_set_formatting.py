import csv
import json

if __name__ == "__main__":
    max_body = 0
    max_sum = 0
    x = 0
    dict = {}
    with open("TR-DataChallenge1-master/TR-DataChallenge1-master/2-Title_Summarization/test2.csv") as f:
        read = csv.reader(f)
        header = next(read)
        for row in read:
            x += 1
            body = "startseq " + row[1] + " endseq"
            summ = ""
            if x == 2:
                print(body)
                print("sas",summ)
            dict[body] = summ
    # print(dict)

    with open("formatted_data/test.json", "w") as out:
        json.dump(dict, out)
        print(f"Saved {x} entries to ")