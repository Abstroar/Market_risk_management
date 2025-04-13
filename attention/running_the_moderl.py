import tensorflow as tf
import numpy as np
import json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from model import BahdanauAttention, load_tokenizer_from_json  # adjust if needed

# Load model
model_path = '../attention/model/model_checkpoint_20.keras'
model = load_model(model_path, custom_objects={'BahdanauAttention': BahdanauAttention})

# Load tokenizer
tokenizer = load_tokenizer_from_json('dataset/formatted_data/tokens/tokenizer_full.json')
index_word = tokenizer.index_word
word_index = tokenizer.word_index

# Parameters
max_len_enc = 500
max_len_dec = 15
start_token = word_index.get('startseq', 1)
end_token = word_index.get('endseq', 2)

# Load test data
with open("dataset/formatted_data/test.json", "r") as f:
    test_data = json.load(f)

# Loop through test samples
for test_text in list(test_data.keys()):
    print("\nInput:", test_text)

    # Encode input
    encoder_input_seq = tokenizer.texts_to_sequences([test_text])[0]
    if not encoder_input_seq:
        print("⚠️ Skipping: produced empty token sequence.")
        continue

    encoder_input = pad_sequences([encoder_input_seq], maxlen=max_len_enc, padding='post')

    # Decoder init
    decoder_input_seq = [start_token]
    output_sentence = []

    for _ in range(max_len_dec):
        padded_decoder_input = pad_sequences([decoder_input_seq], maxlen=max_len_dec, padding='post')
        predictions = model.predict([encoder_input, padded_decoder_input], verbose=0)
        predicted_token_id = np.argmax(predictions[0, len(decoder_input_seq) - 1])

        if predicted_token_id == end_token:
            break

        output_sentence.append(index_word.get(predicted_token_id, '<unk>'))
        decoder_input_seq.append(predicted_token_id)

    print("Generated:", ' '.join(output_sentence))
