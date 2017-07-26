import csv
import os
import matplotlib.pyplot as plt

DATA_DIR = "data/classification"

class Data:
    csv_name = None
    csv_reader = None
    training_data = None
    test_data = None

    def __init__(self, file):
        self.csv_name = file
        assert os.path.isfile(DATA_DIR + '/' + file)
        self.csv_reader = csv.reader(open(self.csv_name))

    def read_from_csv(self):
        self.test_data = []
        assert self.csv_reader is not None
        # for row in self.csv_reader:
            