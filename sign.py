from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np


class Sign:
    def __init__(self, user, pattern_id, valid_sign):
        self.user = user
        self.pattern_id = pattern_id
        self.valid_sign = valid_sign
        self.position = defaultdict(list)
        self.delta_t = []
        self.acc = defaultdict(list)
        self.gyr = defaultdict(list)
        self.valid_sample = None

    def add_single_row(self, row):
        self.position['x'].append(float(row[2]))
        self.position['y'].append(float(row[3]))
        self.delta_t.append(int(row[5]))
        self.acc['x'].append(float(row[6]))
        self.acc['y'].append(float(row[7]))
        self.acc['z'].append(float(row[8]))
        self.gyr['x'].append(float(row[9]))
        self.gyr['y'].append(float(row[10]))
        self.gyr['z'].append(float(row[11]))

    def set_pattern_id(self, value):
        self.pattern_id = value

    def set_valid_state(self, valid):
        self.valid_sign = valid

    def set_position(self, positon):
        self.position = positon

    def set_delta_t(self, delta_t):
        self.delta_t = delta_t

    def set_acc(self, acc):
        self.acc = acc

    def set_gyr(self, gyr):
        self.gyr = gyr

    def get_csv_row(self, index):
        row = [self.user, self.pattern_id,
               self.position['x'][index], self.position['y'][index],
               self.delta_t[index], index,
               self.acc['x'][index], self.acc['y'][index], self.acc['z'][index],
               self.gyr['x'][index], self.gyr['y'][index], self.gyr['z'][index],
               self.valid_sign]
        return row

    def get_pattern_size(self):
        return len(self.delta_t)

    def get_user(self):
        return self.user

    def get_pattern_id(self):
        return self.pattern_id

    def get_valid_sign(self):
        return self.valid_sign

    def get_position(self):
        return self.position

    def get_delta_t(self):
        return self.delta_t

    def get_acc(self):
        return self.acc

    def get_gyr(self):
        return self.gyr

    def plot_gyr(self, time=[], new_values=[]):
        if not new_values:
            new_values = self.gyr

        if not time:
            time = self.delta_t

        plt.subplot(1, 3, 1)
        plt.plot(self.delta_t, self.gyr['x'], label="input", marker='o')
        plt.plot(time, new_values['x'], label="output", marker='x')
        plt.ylabel('x')
        plt.xlabel('t')
        plt.legend()

        plt.subplot(1, 3, 2)
        plt.plot(self.delta_t, self.gyr['y'], label="input", marker='o')
        plt.plot(time, new_values['y'], label="output", marker='x')
        plt.ylabel('y')
        plt.xlabel('t')
        plt.legend()

        plt.subplot(1, 3, 3)
        plt.plot(self.delta_t, self.gyr['z'], label="input", marker='o')
        plt.plot(time, new_values['z'], label="output", marker='x')
        plt.xlabel('t')
        plt.legend()
        plt.show()

    def plot_gyr_2(self, time=[], new_values=[]):
        if not new_values:
            new_values = self.gyr

        if not time:
            time = self.delta_t

        plt.subplot(2, 1, 1)
        plt.plot(self.delta_t, self.gyr['x'], label="x", marker='x')
        plt.plot(self.delta_t, self.gyr['y'], label="y", marker='x')
        plt.plot(self.delta_t, self.gyr['z'], label="z", marker='x')
        plt.yticks(np.arange(-4, 4, step=1))
        plt.xlabel('t')
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(time, new_values['x'], label="x", marker='x')
        plt.plot(time, new_values['y'], label="y", marker='x')
        plt.plot(time, new_values['z'], label="z", marker='x')
        plt.yticks(np.arange(-4, 4, step=1))
        plt.xlabel('t')
        plt.legend()
        plt.show()

    def plot_acc(self, time=[], new_values=[]):
        if not new_values:
            new_values = self.acc

        if not time:
            time = self.delta_t

        plt.subplot(1, 3, 1)
        plt.plot(self.delta_t, self.acc['x'], label="input", marker='o')
        plt.plot(time, new_values['x'], label="output", marker='x')
        plt.ylabel('x')
        plt.xlabel('t')
        plt.legend()

        plt.subplot(1, 3, 2)
        plt.plot(self.delta_t, self.acc['y'], label="input", marker='o')
        plt.plot(time, new_values['y'], label="output", marker='x')
        plt.ylabel('y')
        plt.xlabel('t')
        plt.legend()

        plt.subplot(1, 3, 3)
        plt.plot(self.delta_t, self.acc['z'], label="input", marker='o')
        plt.plot(time, new_values['z'], label="output", marker='x')
        plt.ylabel('z')
        plt.xlabel('t')
        plt.legend()
        plt.show()

    def plot_acc_2(self, time=[], new_values=[]):
        if not new_values:
            new_values = self.acc

        if not time:
            time = self.delta_t

        plt.subplot(2, 1, 1)
        plt.plot(self.delta_t, self.acc['x'], label="x", marker='x')
        plt.plot(self.delta_t, self.acc['y'], label="y", marker='x')
        plt.plot(self.delta_t, self.acc['z'], label="z", marker='x')
        plt.yticks(np.arange(-20, 21, step=10))
        plt.xlabel('t')
        plt.legend()

        plt.subplot(2, 1, 2)
        plt.plot(time, new_values['x'], label="x", marker='x')
        plt.plot(time, new_values['y'], label="y", marker='x')
        plt.plot(time, new_values['z'], label="z", marker='x')
        plt.yticks(np.arange(-20, 21, step=10))
        plt.xlabel('t')
        plt.legend()
        plt.show()

    def plot_sign_xy(self, title=''):
        plt.title(title)
        if self.valid_sample is None:
            plt.plot(self.position['x'], self.position['y'], marker='x', markeredgecolor="red")
        else:
            plt.plot(self.position['x'], self.position['y'])
            for i, valid in enumerate(self.valid_sample):
                if valid:
                    plt.plot(self.position['x'][i], self.position['y'][i], marker='.', color="blue")
                else:
                    plt.plot(self.position['x'][i], self.position['y'][i], marker='x', color="red")

        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()

    def plot_2signs_xy(self, title='', new_sign=None):
        plt.title(title)
        plt.plot(self.position['x'], self.position['y'], linewidth=2, marker='.', color="limegreen")

        new_position = new_sign.get_position()
        plt.plot(new_position['x'], new_position['y'], linewidth=1, marker='x', color="red")

        plt.xlabel('x')
        plt.ylabel('y')
        plt.show()

    def plot_sign_t(self, title='', time=[]):
        plt.title(title)
        plt.plot(self.delta_t, self.position['x'], marker='.', label="input")
        if time:
            plt.plot(time, self.position['x'], marker='x', label="output")
        plt.xlabel('t')
        plt.ylabel('x')
        plt.legend()
        plt.show()
