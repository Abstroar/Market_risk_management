import csv


if __name__ == "__main__":
    max_body = 0
    max_sum = 0
    x = 0
    with open("dataset/TR-DataChallenge1-master/TR-DataChallenge1-master/2-Title_Summarization/train2.csv") as f:
        read = csv.reader(f)
        for row in read:
            x += 1
            max_body = max(max_body,len(row[1].split()))
            max_sum = max(max_sum, len(row[2].split()))
            print(row)

    print("max",x,max_body,max_sum)