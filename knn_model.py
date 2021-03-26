import numpy as np


def hamming_distance(X, X_train):
    """
    Zwraca odległość Hamminga dla obiektów ze zbioru *X* od obiektów z *X_train*.

    :param X: zbiór porównywanych obiektów N1xD
    :param X_train: zbiór obiektów do których porównujemy N2xD
    :return: macierz odległości pomiędzy obiektami z "X" i "X_train" N1xN2
    """

    X = X.toarray()
    X_train = X_train.toarray()

    X_train = X_train.transpose()
    outArr = X.astype(np.uint8) @ X_train.astype(np.uint8)
    outArr2 = (~X).astype(np.uint8) @ (~X_train).astype(np.uint8)
    arr = outArr + outArr2

    return np.subtract(np.uint8(X_train.shape[0]), arr)


def sort_train_labels_knn(Dist, y):
    """
    Sortuje etykiety klas danych treningowych *y* względem prawdopodobieństw
    zawartych w macierzy *Dist*.

    :param Dist: macierz odległości pomiędzy obiektami z "X" i "X_train" N1xN2
    :param y: wektor etykiet o długości N2
    :return: macierz etykiet klas posortowana względem wartości podobieństw
        odpowiadającego wiersza macierzy Dist N1xN2

    """
    w = Dist.argsort(kind='mergesort')
    return y[w]


def p_y_x_knn(y, k):
    """
    Wyznacza rozkład prawdopodobieństwa p(y|x) każdej z klas dla obiektów
    ze zbioru testowego wykorzystując klasyfikator KNN wyuczony na danych
    treningowych.

    :param y: macierz posortowanych etykiet dla danych treningowych N1xN2
    :param k: liczba najbliższych sasiadow dla KNN
    :return: macierz prawdopodobieństw p(y|x) dla obiektów z "X" N1xM
    """

    points_number = 5               # liczba możliwych klas
    result_matrix = []
    for i in range(np.shape(y)[0]):
        helper = []
        for j in range(k):
            helper.append(y[i][j])
        line = np.bincount(helper, None, points_number)
        result_matrix.append([line[0] / k, line[1] / k, line[2] / k, line[3] / k, line[4] / k])
    return result_matrix


def classification_error(p_y_x, y_true):
    """
    Wyznacza błąd klasyfikacji.

    :param p_y_x: macierz przewidywanych prawdopodobieństw - każdy wiersz
        macierzy reprezentuje rozkład p(y|x) NxM
    :param y_true: zbiór rzeczywistych etykiet klas 1xN
    :return: błąd klasyfikacji
    """
    n = len(p_y_x)
    m = len(p_y_x[0])
    res = 0
    for i in range(0, n):
        if (m - np.argmax(p_y_x[i][::-1]) - 1) != y_true[i]:
            res += 1
    return res / n


def model_selection_knn(X_val, X_train, y_val, y_train, k_values):
    """
    Wylicza bład dla różnych wartości *k*. Dokonuje selekcji modelu KNN
    wyznaczając najlepszą wartość *k*, tj. taką, dla której wartość błędu jest
    najniższa.

    :param X_val: zbiór danych walidacyjnych N1xD
    :param X_train: zbiór danych treningowych N2xD
    :param y_val: etykiety klas dla danych walidacyjnych 1xN1
    :param y_train: etykiety klas dla danych treningowych 1xN2
    :param k_values: wartości parametru k, które mają zostać sprawdzone
    :return: krotka (best_error, best_k, errors), gdzie "best_error" to
        najniższy osiągnięty błąd, "best_k" to "k" dla którego błąd był
        najniższy, a "errors" - lista wartości błędów dla kolejnych
        "k" z "k_values"
    """
    k = len(k_values)
    errors = []
    Dist = hamming_distance(X_val, X_train)
    ksort = sort_train_labels_knn(Dist, y_train)
    for i in range(0, k):
        error = classification_error(p_y_x_knn(ksort, k_values[i]), y_val)
        errors.append(error)
    best_error = min(errors)
    best_k = k_values[np.argmin(errors)]
    return best_error, best_k, errors