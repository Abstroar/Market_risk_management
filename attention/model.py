import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import Sequence
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.preprocessing.text import Tokenizer
import numpy as np
import json
from tensorflow.keras.callbacks import EarlyStopping

class BahdanauAttention(tf.keras.layers.Layer):
    def __init__(self, units, **kwargs):
        super(BahdanauAttention, self).__init__(**kwargs)
        self.units = units
        self.W1 = tf.keras.layers.Dense(units)
        self.W2 = tf.keras.layers.Dense(units)
        self.V = tf.keras.layers.Dense(1)

    def call(self, query, values):
        # query: Decoder hidden state at t (batch_size, hidden size)
        # values: Encoder outputs (batch_size, time_steps, hidden size)
        query_with_time_axis = tf.expand_dims(query, 1)
        score = self.V(tf.nn.tanh(self.W1(query_with_time_axis) + self.W2(values)))

        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights

    def get_config(self):
        # This method is required for Keras to serialize and save/load the layer
        config = super(BahdanauAttention, self).get_config()
        config.update({
            'units': self.units,
        })
        return config

def build_attention_seq2seq_model(
    vocab_size_enc,
    vocab_size_dec,
    embedding_dim=256,
    lstm_units=512,
    max_len_enc=300,
    max_len_dec=15
):
    # Encoder
    encoder_inputs = Input(shape=(max_len_enc,))
    enc_emb = Embedding(input_dim=vocab_size_enc, output_dim=embedding_dim, mask_zero=True)(encoder_inputs)
    encoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
    encoder_outputs, state_h, state_c = encoder_lstm(enc_emb)

    # Decoder
    decoder_inputs = Input(shape=(max_len_dec,))
    dec_emb = Embedding(input_dim=vocab_size_dec, output_dim=embedding_dim, mask_zero=True)(decoder_inputs)
    decoder_lstm = LSTM(lstm_units, return_state=True)

    # Attention
    attention = BahdanauAttention(lstm_units)

    all_outputs = []
    decoder_state_h, decoder_state_c = state_h, state_c
    decoder_inputs_step = tf.expand_dims(dec_emb[:, 0, :], 1)

    for t in range(max_len_dec):
        context_vector, attn_weights = attention(decoder_state_h, encoder_outputs)
        context_vector = tf.expand_dims(context_vector, 1)
        dec_input_concat = Concatenate(axis=-1)([context_vector, decoder_inputs_step])
        output, decoder_state_h, decoder_state_c = decoder_lstm(dec_input_concat, initial_state=[decoder_state_h, decoder_state_c])
        output = Dense(vocab_size_dec, activation='softmax')(output)
        all_outputs.append(output)

        # Move to next timestep input
        if t + 1 < max_len_dec:
            decoder_inputs_step = dec_emb[:, t + 1:t + 2, :]

    decoder_outputs = tf.stack(all_outputs, axis=1)

    # Compile model
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    return model

# def load_tokenizer_from_json(json_file_inp='formatted_data/tokens/tokenizer_inp.json',json_file_out='formatted_data/tokens/tokenizer_inp.json'):
#     with open(json_file_inp, "r", encoding="utf-8") as f:
#         word_index1 = json.load(f)
#     with open(json_file_out, "r", encoding="utf-8") as f:
#         word_index2 = json.load(f)
#
#     tok1 = Tokenizer(num_words=10000, oov_token="<unk>")
#     tok2 = Tokenizer(num_words=10000, oov_token="<unk>")
#     tok1.word_index = word_index1
#     tok1.index_word = {i: w for w, i in word_index1.items()}
#     tok2.word_index = word_index2
#     tok2.index_word = {i: w for w, i in word_index2.items()}
#     return tok1,tok2
def load_tokenizer_from_json(json_file='attention/dataset/formatted_data/tokens/tokenizer_full.json'):
    with open(json_file, "r", encoding="utf-8") as f:
        word_index = json.load(f)
    tok1 = Tokenizer(num_words=10000, oov_token="<unk>")
    tok1.word_index = word_index
    tok1.index_word = {i: w for w, i in word_index.items()}
    return tok1
class CaptionDataGenerator(Sequence):
    def __init__(self, data, tokenizer, vocab_size, max_len_enc, max_len_dec, batch_size=32):
        self.data_items = [(a, b) for a, b in data.items()]
        self.vocab_size = vocab_size
        self.batch_size = batch_size
        self.tokenizer = tokenizer

        self.max_len_enc =  max_len_enc
        self.max_len_dec = max_len_dec

    def __len__(self):
        return int(np.ceil(len(self.data_items))/self.batch_size)

    def __getitem__(self, ind):
        batch_items = self.data_items[ind * self.batch_size : (ind + 1) * self.batch_size]
        encoder_input_data = []
        decoder_input_data = []
        decoder_output_data = []

        for a,b in batch_items:
            inp = self.tokenizer.texts_to_sequences([a])[0]
            out = self.tokenizer.texts_to_sequences([b])[0]
            # print("ab",a,b)
            # print("inp,out",inp,out)
            enc_seq = pad_sequences([inp], maxlen = self.max_len_enc, padding="post")[0]
            dec_seq = pad_sequences([out], maxlen=self.max_len_dec, padding="post")[0]
            decoder_input = dec_seq[:-1]
            decoder_output = dec_seq[1:]

            decoder_input = pad_sequences([decoder_input], maxlen=self.max_len_dec, padding='post')[0]
            decoder_output = pad_sequences([decoder_output], maxlen=self.max_len_dec, padding='post')[0]

            encoder_input_data.append(enc_seq)
            decoder_input_data.append(decoder_input)
            decoder_output_data.append(decoder_output)

        return [np.array(encoder_input_data), np.array(decoder_input_data)], np.expand_dims(np.array(decoder_output_data), -1)


if __name__ == "__main__":
    max_length = 20
    vocabulary_size = 10000
    embedding_dim = 200
    batch_size = 64
    tok1 = load_tokenizer_from_json()
    data = {}
    model = build_attention_seq2seq_model(vocabulary_size,vocabulary_size,embedding_dim,lstm_units=128,max_len_enc=500,max_len_dec=15)
    with open("attention/dataset/formatted_data/train.json", 'r') as f:
        data = json.load(f)
    generate = CaptionDataGenerator(data, tokenizer=tok1, vocab_size=10000, max_len_enc=500, max_len_dec=15)
    print(generate[0])
    model.summary()
    checkpoint = ModelCheckpoint(
        filepath='attention/model/model_checkpoint_{epoch:02d}.keras',
        save_best_only=False,
        save_weights_only=False,
        verbose=1
    )
    early_stop = EarlyStopping(
        monitor='loss',  # Ideally, use 'val_loss' if you have validation data
        patience=3,
        restore_best_weights=True
    )
    model.fit(generate, epochs=20, callbacks=[checkpoint, early_stop])

