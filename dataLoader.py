from collections import defaultdict

import csv
import numpy as np


class DataLoader:
    def __init__(self, file_path, width=None):
        self.file_path = file_path
        self.width = width
        self.screen_resolution = {'x': 1080, 'y': 2340}

    def get_data(self, augmented_data_paths=None):
        width = 0
        in_data = defaultdict(list)
        out_data = defaultdict(list)

        readfile = open(self.file_path, mode='r', newline='')
        csv_reader = csv.reader(readfile)
        next(csv_reader) #skip the header

        for row in csv_reader:
            in_data, out_data = self.add_data_to_dict(in_data, out_data, row)

            if len(in_data[int(row[1])]) > width:
                width = len(in_data[int(row[1])])

        original_signs = len(out_data.keys())

        if augmented_data_paths:
            for augmented_data in augmented_data_paths:
                readfile = open(augmented_data, mode='r', newline='')
                csv_reader = csv.reader(readfile)
                keys = list(in_data.keys())
                padding = keys[-1]+1

                for row in csv_reader:
                    in_data, out_data = self.add_data_to_dict(in_data, out_data, row, padding)

                    if len(in_data[int(row[1])+padding]) > width:
                        width = len(in_data[int(row[1])])

        keys = list(out_data.keys())
        height = len(keys)

        if self.width:
            width = self.width*9

        in_array = np.zeros([height, int(width)])
        out_array = np.zeros(height)
        for i, key in enumerate(keys):
            in_array[i, :len(in_data[key])] = np.asarray(in_data[key])
            out_array[i] = out_data[key]

        t_max = 0
        acc_max = 0
        gyr_max = 0

        final_array = []

        for sequence in in_array:
            x = sequence[0::9]
            y = sequence[1::9]
            t = sequence[2::9]
            acc_x = sequence[3::9]
            acc_y = sequence[4::9]
            acc_z = sequence[5::9]
            gyr_x = sequence[6::9]
            gyr_y = sequence[7::9]
            gyr_z = sequence[8::9]

            abs(np.concatenate((acc_x, acc_y, acc_z)))

            if max(t) > t_max:
                t_max = max(t)

            max_value = self.get_max_value(acc_x, acc_y, acc_z)
            if max_value > acc_max:
                acc_max = max_value

            max_value = self.get_max_value(gyr_x, gyr_y, gyr_z)
            if max_value > gyr_max:
                gyr_max = max_value

            array = np.asarray([x, y, t, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z])

            final_array.append(array)

        for array in final_array:
            for i, (x, y, t, acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z) in enumerate(zip(array[0], array[1], array[2],
                                                                                        array[3], array[4], array[5],
                                                                                        array[6], array[7], array[8])):
                array[0][i] = x / self.screen_resolution['x']
                array[1][i] = y / self.screen_resolution['y']
                array[2][i] = t / t_max
                array[3][i] = acc_x / acc_max
                array[4][i] = acc_y / acc_max
                array[5][i] = acc_z / acc_max
                array[6][i] = gyr_x / gyr_max
                array[7][i] = gyr_y / gyr_max
                array[8][i] = gyr_z / gyr_max

        final_array = np.asarray(final_array)

        if augmented_data_paths:
            return final_array[:original_signs], out_array[:original_signs], final_array[original_signs:], out_array[original_signs:]
        else:
            return final_array, out_array, [], []

    def add_data_to_dict(self, in_data, out_data, row, padding=0):
        # position
        in_data[int(row[1])+padding].append(float(row[2]))
        in_data[int(row[1])+padding].append(float(row[3]))
        # time
        in_data[int(row[1])+padding].append(float(row[5]))
        # acc
        in_data[int(row[1])+padding].append(float(row[6]))
        in_data[int(row[1])+padding].append(float(row[7]))
        in_data[int(row[1])+padding].append(float(row[8]))
        # gyr
        in_data[int(row[1])+padding].append(float(row[9]))
        in_data[int(row[1])+padding].append(float(row[10]))
        in_data[int(row[1])+padding].append(float(row[11]))

        out_data[int(row[1])+padding] = np.array([1]) if row[12].lower() == "true" else np.array([0])
        return in_data, out_data

    def get_max_value(self, acc_x, acc_y, acc_z):
        return max(abs(np.concatenate((acc_x, acc_y, acc_z))))
