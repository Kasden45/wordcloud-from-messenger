import fnmatch
import json
import os
import re
import pickle
import random
from knn_model import *

import numpy as np
from scipy import sparse
from stempel import StempelStemmer


class TextAnalyzer():
    def __init__(self, initiate=True):

        if initiate:
            self.stemmer = StempelStemmer.polimorf()
            self.allwords = []

            self.train_mtx = None
            self.val_mtx = None
            self.test_mtx = None

            self.y_train = None
            self.y_val = None
            self.y_test = None

            self.best_k = None

    def print_all_data(self):
        print("AllWords:", self.allwords)

        print("TrainX:", self.train_mtx)
        print("ValX:", self.val_mtx)
        print("TestX:", self.test_mtx)

        print("TrainY:", self.y_train)
        print("ValY:", self.y_val)
        print("TestY:", self.y_test)

    def top20_from_categories(self):
        results = []
        chosen_words = load_words_to_check()
        for category in chosen_words:
            sorted_slownik = {k: v for k, v in
                              sorted(chosen_words[category].items(), key=lambda item: item[1], reverse=True)}
            print("Nazwa: ", category)
            words_array = []
            i = 0
            for key_word in sorted_slownik:

                if i == 20:
                    break
                i += 1
                words_array.append(key_word)
            results += words_array
            print("Top20 from", category, ":", words_array)
        print(results)
        self.allwords = results  # stores all words to be checked

    def matrix_from_data(self, training_messages, mode="train"):  # mode = "train", "val", "test"
        row_arr = []
        col_arr = []
        data_arr = []
        ys = []
        counter = 0
        for message in training_messages:
            print("Mode = {}, {}. wiadomosc:".format(mode, counter))
            training_array, typ_wiadomosci = self.add_training_message(message)
            ys.append(typ_wiadomosci)
            indeksy = [i for i, val in enumerate(training_array) if val == True]
            print("Wiadomość:", message, "Indeksy: ", indeksy)
            for index in indeksy:
                row_arr.append(counter)
                col_arr.append(index)
                data_arr.append(True)
            counter += 1
        row = np.array(row_arr)
        col = np.array(col_arr)
        data = np.array(data_arr)
        mtx = sparse.csc_matrix((data, (row, col)), shape=(counter, len(self.allwords)))
        if mode == "train":
            self.train_mtx = mtx
            self.y_train = ys
            print("TRAIN MTX: ", self.train_mtx)
            print("YTRAIN: ", ys)
        elif mode == "val":
            self.val_mtx = mtx
            self.y_val = ys
            print("VAL MTX: ", self.val_mtx)
            print("YTRAIN: ", ys)
        elif mode == "test":
            self.test_mtx = mtx
            self.y_test = ys
            print("TEST MTX: ", self.test_mtx)
            print("YTRAIN: ", ys)

    def add_training_message(self, message):
        print("\nWiadomość:", message)
        try:
            wybor = int(input("\n0 - szczęście,\n1 - zaskoczenie,\n2 - neutralne,\n3 - smutek,\n4 - złość\n:  "))
        except:
            print("Nie wybrales, trudno")
            wybor = 2
        message_array = [False] * len(self.allwords)  # wektor [0, 0, 0, 0, ... 0, 0, 0]
        for word in re.split('; |, |\*|\n| |\u00e2\u0080\u009d|\u00e2\u0080\u009e|:\)|\)', message):
            if len(word) > 0:
                word = self.stemmer.stem(word.lower())
                if word in self.allwords:
                    number = self.allwords.index(word)
                    message_array[number] = True

        return message_array, wybor  # wektor [0,0,0, ... 1, ... 0, 1]

    def save_to_file(self):
        try:
            with open("{}.pkl".format(input("Nazwa pliku zapisu:")), "wb") as f:
                pickle.dump(self, f)
        except Exception as e:
            print(e)

    def load_from_file(self, file=None):
        try:
            with open("{}.pkl".format(input("Nazwa pliku do odczytu:") if file is None else file), "rb") as f:
                loaded = pickle.load(f)
                self.stemmer = loaded.stemmer
                self.allwords = loaded.allwords
                self.best_k = loaded.best_k
                self.test_mtx = loaded.test_mtx
                self.train_mtx = loaded.train_mtx
                self.val_mtx = loaded.val_mtx

                self.y_val = loaded.y_val
                self.y_train = loaded.y_train
                self.y_test = loaded.y_test
                print("-----------------------------------------------\n" +
                      "-------------------DATA LOADED-----------------\n" +
                      "-----------------------------------------------")
                self.print_all_data()
        except Exception as e:
            print(e)

    def analyze_many_messages(self, messages):
        counter = 0
        row_arr = []
        col_arr = []
        data_arr = []

        for message in messages:
            message_array = [False] * len(self.allwords)  # wektor [0, 0, 0, 0, ... 0, 0, 0]
            message = message.encode('raw_unicode_escape').decode('utf8')
            if len(message) < 15:
                continue
            for word in re.split('; |, |\*|\n| |\u00e2\u0080\u009d|\u00e2\u0080\u009e|:\)|\)', message):
                if len(word) > 0:
                    word = self.stemmer.stem(word.lower())
                    if word in self.allwords:
                        number = self.allwords.index(word)
                        message_array[number] = True
            indeksy = [i for i, val in enumerate(message_array) if val == True]

            if len(indeksy) > 0:
                #print("Wiadomość:", message, "Indeksy: ", indeksy)
                for index in indeksy:
                    row_arr.append(counter)
                    col_arr.append(index)
                    data_arr.append(True)
                counter += 1

        row = np.array(row_arr)
        col = np.array(col_arr)
        data = np.array(data_arr)
        mtx = sparse.csc_matrix((data, (row, col)), shape=(counter, len(self.allwords)))
        #print("MTX", mtx)
        if len(data) == 0:
            return {}
        Dist = hamming_distance(mtx,
                                self.train_mtx)  # wyliczenie odległości między każdym testowym i treningowym
        y_sorted = sort_train_labels_knn(Dist, np.array(self.y_train,
                                                        dtype=np.uint8))  # posortowana macierz odległości
        #print("y sorted:", y_sorted)
        p_y_x = p_y_x_knn(y_sorted, self.best_k)  # rozkład p-stw przynależności do róznych grup

        #print(p_y_x)
        result = []
        for sentence in p_y_x:
            result.append(sentence.index(max(sentence)))
        dictionary_classes = {}
        classes = ["szczęście", "rozbawienie", "neutralne", "smutek", "złość"]
        for i in range(5):
            dictionary_classes[classes[i]] = sum(p == i for p in result)
        return dictionary_classes


def determine_words_to_check(lista_wiadomosci):
    stemer = StempelStemmer.polimorf()
    slownik = {
        "szczęście": {},
        "rozbawienie": {},
        "neutralne": {},
        "smutek": {},
        "złość": {}}
    counter=0
    for wiadomosc in lista_wiadomosci:
        counter += 1
        print("{}. wiadomość:\n".format(counter), wiadomosc)
        try:
            wybor = int(input("\n0 - szczęście,\n1 - zaskoczenie,\n2 - neutralne,\n3 - smutek,\n4 - złość\n:  "))
        except:
            print("Nie wybrano wartosci")
            continue

        if 0 > wybor > 5:
            continue
        for word in re.split('; |, |\*|\n| |\u00e2\u0080\u009d|\u00e2\u0080\u009e|:\)|\)', wiadomosc):
            if len(word) > 2:
                stemmed = stemer.stem(word.lower())
                if wybor == 0:
                    if stemmed in slownik["szczęście"].keys():
                        slownik["szczęście"][stemmed] += 1
                    else:
                        slownik["szczęście"][stemmed] = 1  # [słowo, wystąpienia]
                elif wybor == 1:
                    if stemmed in slownik["rozbawienie"].keys():
                        slownik["rozbawienie"][stemmed] += 1
                    else:
                        slownik["rozbawienie"][stemmed] = 1  # [słowo, wystąpienia]
                elif wybor == 2:
                    if stemmed in slownik["neutralne"].keys():
                        slownik["neutralne"][stemmed] += 1
                    else:
                        slownik["neutralne"][stemmed] = 1  # [słowo, wystąpienia]
                elif wybor == 3:
                    if stemmed in slownik["smutek"].keys():
                        slownik["smutek"][stemmed] += 1
                    else:
                        slownik["smutek"][stemmed] = 1  # [słowo, wystąpienia]
                elif wybor == 4:
                    if stemmed in slownik["złość"].keys():
                        slownik["złość"][stemmed] += 1
                    else:
                        slownik["złość"][stemmed] = 1  # [słowo, wystąpienia]
    try:
        with open("chosen_words.pkl", "wb") as f:
            pickle.dump(slownik, f)
    except Exception as e:
        print(e)


def load_words_to_check():
    try:
        with open("chosen_words.pkl", "rb") as f:
            wczytany_slownik = pickle.load(f)
    except Exception as e:
        print(e)
    return wczytany_slownik


def create_messages_from_inbox(limit=3000):
    msg_array = []
    counter = 0
    for _, dirs, _ in os.walk("TESTY_WIADOMOSCI/Facebook_New/inbox"):  # singlePersonPATH,dir,filename
        for dir in dirs:
            for _, dirs2, filenames in os.walk("%s/%s" % ("TESTY_WIADOMOSCI/Facebook_New/inbox", dir)):
                for filename in filenames:
                    if fnmatch.fnmatch(filename, 'message*'):
                        with open("TESTY_WIADOMOSCI/Facebook_New/inbox/" + dir + "/" + filename, 'r',
                                  encoding="utf8") as file:
                            filedata = file.read()
                            data = json.loads(filedata)
                        for message in data["messages"]:
                            a = random.randint(1, 400)
                            if a == 50:
                                if counter != limit:
                                    if "content" in message:

                                        msg = message["content"].encode('raw_unicode_escape').decode('utf8')
                                        if len(msg) > 40 and not (msg.startswith("www") or msg.startswith("http")):   # minimalna długość wiadomosci
                                            counter += 1
                                            msg_array.append(msg)
                                else:
                                    print("MSG ARRAY: ", msg_array)
                                    print("dlugosc", len(msg_array))
                                    random.shuffle(msg_array)
                                    return msg_array
    print("MSG ARRAY: ", msg_array)
    print("dlugosc", len(msg_array))
    random.shuffle(msg_array)
    return msg_array


def create_model(text_analyzer):
    # KNN model selection
    k_values = range(1, len(text_analyzer.y_train), 2)
    print('\n------------- Selekcja liczby sasiadow dla modelu dla KNN -------------')
    text_analyzer.print_all_data()
    error_best, best_k, errors = model_selection_knn(text_analyzer.val_mtx,
                                                     text_analyzer.train_mtx,
                                                     np.array(text_analyzer.y_val, dtype=np.uint8),
                                                     np.array(text_analyzer.y_train, dtype=np.uint8),
                                                     k_values)
    print('Najlepsze k: {num1} i najlepszy blad: {num2:.4f}'.format(num1=best_k, num2=error_best))

    Dist = hamming_distance(text_analyzer.test_mtx, text_analyzer.train_mtx)  # wyliczenie odległości między każdym testowym i treningowym
    y_sorted = sort_train_labels_knn(Dist, np.array(text_analyzer.y_train, dtype=np.uint8))  # posortowana macierz odległości
    p_y_x = p_y_x_knn(y_sorted, best_k)  # rozkład p-stw przynależności do róznych grup
    print("Rozkład P-stw:", p_y_x)

    error_KNN = classification_error(p_y_x, np.array(text_analyzer.y_test, dtype=np.uint8))
    print("Error KNN: ", error_KNN)

    return best_k


if __name__ == "__main__":
    flag = True
    if flag:
        determine_words_to_check(create_messages_from_inbox()[:30])      # wybieranie słów z bazy iluś znalezionych zdań

        ta = TextAnalyzer()                                             # tworzenie obiektu
        ta.top20_from_categories()                                       # wyciąganie słów z odpowiedniego pliku
        ta.matrix_from_data(create_messages_from_inbox()[:50], "train")  # tworzenie ciągu treningowego
        ta.matrix_from_data(create_messages_from_inbox()[:50], "val")    # tworzenie ciągu walidacyjnego
        ta.matrix_from_data(create_messages_from_inbox()[:50], "test")   # tworzenie ciągu testowego
        ta.save_to_file()                                                # zapisanie całej klasy do pliku
        ta.print_all_data()

        ta2 = TextAnalyzer()
        ta2.load_from_file()
        ta2.print_all_data()
        ta2.best_k = create_model(ta2)
    else:
        ta2 = TextAnalyzer()
        ta2.load_from_file("model_final")
        ta2.print_all_data()
        ta2.best_k = create_model(ta2)
