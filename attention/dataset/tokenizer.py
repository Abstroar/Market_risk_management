import csv

import json
import pickle
from tensorflow.keras.preprocessing.text import Tokenizer


def tokenize_and_save(text_data, json_file='formatted_data/tokens/tokenizer_full.json', pickle_file='formatted_data/tokens/tokenizer_full.pkl'):
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(text_data)
    vocab = tokenizer.word_index

    with open(json_file, 'w', encoding='utf-8') as json_out:
        json.dump(vocab, json_out)

    # Save the tokenizer as a Pickle file
    with open(pickle_file, 'wb') as pickle_out:
        pickle.dump(vocab, pickle_out)

    return tokenizer


def load_tokenizer_from_json(json_file='formatted_data/tokens/tokenizer_inp.json'):
    with open(json_file, "r", encoding="utf-8") as f:
        word_index = json.load(f)

    tok = Tokenizer(num_words=5000, oov_token="<unk>")
    tok.word_index = word_index
    tok.index_word = {i: w for w, i in word_index.items()}
    return tok


def load_tokenizer_from_pickle(pickle_file='tokenizer.pkl'):
    # Load tokenizer from the saved Pickle file
    with open(pickle_file, 'rb') as pickle_in:
        tokenizer = pickle.load(pickle_in)
    return tokenizer


def tokenize_new_input(new_text, tokenizer):
    # Tokenize new input using the loaded tokenizer
    new_sequences = tokenizer.texts_to_sequences(new_text)
    return new_sequences


if __name__ == "__main__":
    text_data = []
    with open("../dataset/TR-DataChallenge1-master/TR-DataChallenge1-master/2-Title_Summarization/train2.csv") as f:
        read = csv.reader(f)
        for row in read:
            text_data.append("startseq " + row[1] + " endseq")
            text_data.append("startseq " + row[2] + " endseq")


    # Tokenize and save to files
    tokenizer= tokenize_and_save(text_data)
    # load_tokenizer_from_json(json_file="formatted_data/tokens/tokenizer_out.json")
    # tok = load_tokenizer_from_json()

    # input_texts_to_tokenize = ["This is a new sentence.", "Tokenization from saved tokenizer."]
    # print(tok.texts_to_sequences(input_texts_to_tokenize))
    # Print tokenized sequences
    # print("Tokenized Sequences:", sequences)

    # Now load the tokenizer from Pickle and use it to tokenize new input
    # loaded_tokenizer = load_tokenizer_from_pickle('tokenizer.pkl')



    # max_body = 0
    # max_sum = 0
    # x = 0
    # with open("dataset/TR-DataChallenge1-master/TR-DataChallenge1-master/2-Title_Summarization/train2.csv") as f:
    #     read = csv.reader(f)
    #     for row in read:
    #         x += 1
    #         max_body = max(max_body,len(row[1].split()))
    #         max_sum = max(max_sum, len(row[2].split()))
    #         print(row)
    #
    # print("max",x,max_body,max_sum)