# wordcloud-from-messenger
## Application that creates word clouds and performes wide analysis based on messenger conversations
## Aplikacja, która tworzy chmury słów i przeprowadza szerokie analizy bazując na kowersacjach messangerowych
### Opis sposobu instalacji i uruchomienia aplikacji 
1.	Pobierz plik/pliki ze swoimi danymi o wiadomościach z serwisu Facebook przy pomocy instrukcji zamieszczonej w pliku o nazwie Help.txt.
2.	Umieść plik „copy_messages.py” w folderze zawierającym katalogi z konwersacjami i uruchom go, wybierając docelowy folder, w którym znajdą się tylko potrzebne informacje z pobranych danych.
3.	Zainstaluj wszystkie potrzebne moduły. Powinny wystarczyć polecenia:
„pip install” X dla X równych: matplotlib, pystempel, pandas, scipy, wordcloud.
4.	Uruchom aplikację, poprzez uruchomienie pliku „main_gui.py” np. komendą python „main_gui.py” znajdując się w głównym katalogu aplikacji. Jeżeli podczas otwierania wystąpi jakiś błąd, to należy doinstalować odpowiednie moduły.

### Installation and launching
1. Download file/files with your messages data from Facebook in JSON format. (tips in Help.txt)
2. Place „copy_messages.py” file in directory containing all conversations and run it to copy required data to another directory
3. Install all required modules:
  matplotlib, pystempel, pandas, scipy, wordcloud
4. Run application by executing  „main_gui.py”. If there were any errors, install required modules

### Funkcjonalności
Aplikacja, korzystając z pobranych wcześniej z serwisu Facebook danych o przeprowadzonych rozmowach, pozwala na wygenerowanie „chmury” z najczęściej używanych wyrazów w wybranej konwersacji lub we wszystkich konwersacjach dla podanego uczestnika. Dodatkowo umożliwia zapisywanie, wczytywanie i usuwanie szablonów oraz historii. Druga zakładka umożliwia użytkownikowi przeanalizowanie szczegółów wszystkich konwersacji i przedstawia wyniki w postaci rankingu. Po wejściu w szczegóły konwersacji, pojawia się okno z posortowanymi malejąco według liczby wiadomości informacjami o uczestniku, średniej długości jego wiadomości oraz liczbie wysłanych wiadomości w konwersacji. Z poziomu tego widoku, użytkownik może:
- zapisać plik ze szczegółami w formacie .txt,
-	zapisać plik ze szczegółami w formacie.csv,
-	wyświetlić najczęściej używane przez uczestników konwersacji reakcje,
-	wyświetlić analizę semantyczną wiadomości każdego z uczestników (procentowy udział wiadomości w 5 ustalonych klasach: szczęście, rozbawienie, neutralne, smutek, złość)
-	wyświetlić wykres średniego czasu odpowiedzi na wiadomości z podziałem na miesiące,
-	wyświetlić wykres liczby wiadomości wysłanych przez każdego z uczestników konwersacji w zależności od miesiąca

### Functionalities
The application lets you generate word cloud from most used words from one conversation (all participants) or all conversations (one participant), based on pre-downloaded facebook files. Additionaly you can save, load or remove settings templates and history.

The second tab lets you analyse details of the conversations and presents the ranking of conversations based on number of messages. You can enter the detailed view of the conversation with average message length by participant, number of messages by participant. From this view you can also:
-	save file with details in .txt format,
-	save file with details in .csv format,
-	view most used reactions by participants,
-	view the semantic analysis of emotions from messages (approx.),
-	view "average response time by month" chart, 
-	view "number of messages by month" chart,
