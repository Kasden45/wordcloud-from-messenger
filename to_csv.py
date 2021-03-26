import csv
import os


def create_report(table_of_dictionaries, name):
    fnames = ["participant_name", "messages", "average_message_length"]
    f = open(f'{os.curdir}/Files/{name}.csv', 'w', newline='')
    with f:
        writer = csv.writer(f)
        writer.writerow(fnames)  # Insert Column names
        for row in table_of_dictionaries:  # Insert values
            writer.writerow(row)
