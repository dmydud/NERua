import os
import csv
import json
import keras
import numpy as np
import pandas as pd
from datetime import datetime
from keras_contrib.layers import CRF
from keras.utils import to_categorical
from keras_contrib.losses import crf_loss
from keras.models import Model, load_model
from keras_contrib.metrics import crf_viterbi_accuracy
from keras.preprocessing.sequence import pad_sequences
from sklearn_crfsuite.metrics import flat_classification_report
from keras.layers import LSTM, Embedding, Dense, TimeDistributed, Bidirectional, Input

from nerua.lang import language as lang_module
from nerua.lang.language import Language
from nerua.tokenizer import tokenize_text
from nerua.stemmer import stem_ukr_word, stem_word


class NNModel:
    def __init__(self, *args, model_id=None, **kwargs):
        self.lang = None
        self._tags = []
        self.stem_words = None
        self.max_words_count_in_sentence = None
        self._model = None

        if model_id is None:
            self._init(*args, **kwargs)

        else:
            self._load(model_id)

    def create(self, train_file_path: str, output_summary: bool = False):
        if not os.path.exists(train_file_path):
            raise FileNotFoundError

        with open(train_file_path, 'r') as train_file:
            self.max_words_count_in_sentence = pd.read_csv(train_file).groupby("article_id").size().max()

        input_layer = Input(shape=(self.max_words_count_in_sentence,))
        word_embedding_size = 150

        model = Embedding(
            input_dim=len(self.lang.vocab),
            output_dim=word_embedding_size,
            input_length=self.max_words_count_in_sentence
        )(input_layer)

        model = Bidirectional(
            LSTM(units=word_embedding_size,
                 return_sequences=True,
                 dropout=0.5,
                 recurrent_dropout=0.5,
                 kernel_initializer=keras.initializers.he_normal())
        )(model)

        model = LSTM(
            units=word_embedding_size * 2,
            return_sequences=True,
            dropout=0.5,
            recurrent_dropout=0.5,
            kernel_initializer=keras.initializers.he_normal()
        )(model)

        model = TimeDistributed(Dense(len(self._tags), activation="relu"))(model)

        crf = CRF(len(self._tags))

        model = Model(input_layer, crf(model))

        model.compile(
            optimizer=keras.optimizers.Adam(lr=0.0005, beta_1=0.9, beta_2=0.999),
            loss=crf.loss_function,
            metrics=[crf.accuracy, 'accuracy']
        )

        if output_summary:
            model.summary()

        self._model = model

    def train(self, file: str, *, val_split: float = .1,
              epoch_count: int = 25, batch_size: int = 256):

        with open(file, 'r') as train_file:
            agg_func = lambda dataframe_part: dataframe_part[["word", "tag"]].values.tolist()
            sentences = pd.read_csv(train_file).groupby("article_id").apply(agg_func)

        input_train_data = pad_sequences(
            maxlen=self.max_words_count_in_sentence,
            sequences=[
                [self.lang.vocab[stem_word(word, self.lang) if self.stem_words else word] for word, _ in sentence]
                for sentence in sentences
            ]
        )

        output_train_data = np.array([
            to_categorical(i, num_classes=len(self._tags))
            for i in pad_sequences(
                maxlen=self.max_words_count_in_sentence,
                sequences=[[self._tags.index(w[1]) for w in s] for s in sentences]
            )
        ])

        history = self._model.fit(
            input_train_data,
            output_train_data,
            batch_size=batch_size,
            epochs=epoch_count,
            validation_split=val_split,
            verbose=2
        )

        return history

    def save(self):
        model_name = f"{self.lang.short_form}_model_{datetime.now().strftime('%d.%m.%YT%H%M%S')}.h5"
        model_dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
        model_path = os.path.join(model_dir_path, "__models__", model_name)

        if not os.path.exists(model_dir_path):
            os.mkdir(model_dir_path)

        with open(os.path.join(model_dir_path, "models_config.csv"), "a") as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([
                hash(model_path),
                type(self.lang).__name__,
                self._tags,
                self.stem_words,
                self.max_words_count_in_sentence,
                model_path
            ])

        if not os.path.exists(os.path.join(model_dir_path, "__models__")):
            os.mkdir(os.path.join(model_dir_path, "__models__"))

        self._model.save(model_path)

        return hash(model_path)

    def predict(self, text, with_report: bool = False):
        prepared_data = [
                [self.lang.vocab[stem_ukr_word(word) if self.stem_words else word] for word in sentence]
                for sentence in tokenize_text(text, self.lang)
            ]
        input_data = pad_sequences(
            maxlen=self.max_words_count_in_sentence,
            sequences=prepared_data
        )

        prediction = self._model.predict(input_data, verbose=1)
        pred_labels = [[self._tags[np.argmax(i)] for i in p][-len(prepared_data[j]):] for j, p in enumerate(prediction)]

        if with_report:
            print(flat_classification_report(y_pred=pred_labels, y_true=pred_labels))

        print(pred_labels)

    def _load(self, model_id):

        model_dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

        model_info = pd.read_csv(
            os.path.join(model_dir_path, "models_config.csv"),
            index_col=0,
            header=None
        ).loc[model_id]

        self.lang, self._tags, self.stem_words, self.max_words_count_in_sentence, model_path = model_info

        self.lang = getattr(lang_module, self.lang)()
        self._tags = json.loads(self._tags.replace("'", '"'))

        self._model = load_model(
            model_path,
            custom_objects={
                'CRF': CRF,
                'crf_loss': crf_loss,
                'crf_viterbi_accuracy': crf_viterbi_accuracy
            }
        )

    def _init(self, lang: Language, stem_words: bool = True):
        self.lang = lang

        label_config_path = os.path.join(os.path.dirname(__file__), "label_config.json")
        if not os.path.exists(label_config_path):
            raise FileNotFoundError

        with open(label_config_path, "r") as label_config_file:
            self._tags = [
                             f'{tag_indicator}-{label_info["text"]}'
                             for label_info in json.load(label_config_file)
                             for tag_indicator in ("B", "I")
                         ] + ["O"]

        self.stem_words = stem_words
        self.max_words_count_in_sentence = None
        self._model = None
