from PyQt5 import QtWidgets, uic
from sign import Sign

import pyqtgraph as pg
import csv
import sys


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('widgets/WidgetT.ui', self)
        self.i = 0
        self.counter = 0
        self.last_x = 0
        self.last_y = 0
        self.last_t = 0
        self.keys = None
        self.reader = None
        self.writer = None
        self.sign = None
        self.all_signs = []
        self.keys_bad = None
        self.open_file_handler()
        self.load_all_signs()
        self.next_pattern()
        self.show()

        self.graphWidget_1.setBackground('w')
        self.graphWidget_2.setBackground('w')

        self.incorrectButton.clicked.connect(self.invalid_sign)
        self.correctButton.clicked.connect(self.valid_sign)

    def open_file_handler(self):
        sign_id = 1
        read_filename = 'data/csv/sign_' + str(sign_id) + '/data_13_09_2020-sign_' + str(sign_id) + '.csv'
        write_filename = 'data/csv/sign_' + str(sign_id) + '/data_13_09_2020-sign_' + str(sign_id) + '-classified_t.csv'

        readfile = open(read_filename, mode='r', newline='')
        self.reader = csv.reader(readfile)
        next(self.reader)  # Skip the header

        writefile = open(write_filename, mode='a', newline='')
        self.writer = csv.writer(writefile, delimiter=',', quotechar='|')
        self.writer.writerow(['user', 'pattern_id', 'pos_x', 'pos_y', 'order_no', 'time', 'acc_x', 'acc_y', 'acc_z',
                              'gyr_x', 'gyr_y', 'gyr_z', 'valid_sign'])

    def load_all_signs(self):
        single_pattern_row = next(self.reader)
        id = single_pattern_row[1]

        while single_pattern_row != "-1":
            sign = Sign(single_pattern_row[0], id, single_pattern_row[12])

            while id == sign.get_pattern_id():
                sign.add_single_row(single_pattern_row)
                single_pattern_row = next(self.reader, "-1")
                id = single_pattern_row[1]

            self.all_signs.append(sign)

    def valid_sign(self):
        self.save_result()
        self.next_pattern()

    def invalid_sign(self):
        self.sign.set_valid_state('False')
        self.save_result()
        self.next_pattern()

    def next_pattern(self):
        if self.counter % 50 == 0:
            self.plot_all_patterns()
        else:
            penPatternSign = pg.mkPen(color=(0, 255, 0), width=1)
            self.graphWidget_1.plot(self.last_t, self.last_x, pen=penPatternSign)
            self.graphWidget_2.plot(self.last_t, self.last_y, pen=penPatternSign)
        valid = False
        while not valid:
            if self.i < len(self.all_signs):
                self.sign = self.all_signs[self.i]
                if self.sign.get_valid_sign() == 'True':
                    penPatternSign = pg.mkPen(color=(0, 0, 255), width=1)
                    self.graphWidget_1.plot(self.sign.get_delta_t(), self.sign.get_position()['x'], pen=penPatternSign)
                    self.graphWidget_2.plot(self.sign.get_delta_t(), self.sign.get_position()['y'], pen=penPatternSign)
                    self.last_x = self.sign.get_position()['x']
                    self.last_y = self.sign.get_position()['y']
                    self.last_t = self.sign.get_delta_t()

                    valid = True
                else:
                    self.save_result()
                print(f"{str(self.i + 1)}/{str(len(self.all_signs))}")
                self.i += 1
            else:
                valid = True
                print("All patterns checked!")
        self.counter = self.counter + 1

    def plot_all_patterns(self):
        self.graphWidget_1.clear()
        self.graphWidget_2.clear()
        for sign in self.all_signs:
            if sign.get_valid_sign() == 'True':
                penPatternSign = pg.mkPen(color=(0, 255, 0), width=1)
                self.graphWidget_1.plot(sign.get_delta_t(), sign.get_position()['x'], pen=penPatternSign)
                self.graphWidget_2.plot(sign.get_delta_t(), sign.get_position()['y'], pen=penPatternSign)

    def save_result(self):
        for i in range(self.sign.get_pattern_size()):
            self.writer.writerow(self.sign.get_csv_row(i))

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
