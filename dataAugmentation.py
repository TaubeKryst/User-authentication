from sign import Sign
from collections import defaultdict
from collections import Counter

import csv
import math
import copy
import random

SIGN = 'sign_1'
AUGMENTATION_TYPE = 1


class DataAugmentation:
    def __init__(self, filename):
        self.lock_write = True
        self.reader = self.open_file_handler(filename)

    def open_file_handler(self, filename):
        readfile = open(filename, mode='r', newline='')
        reader = csv.reader(readfile)
        next(reader)  # Skip the header
        return reader

    def load_all_signs(self):
        all_signs = []
        single_pattern_row = next(self.reader)
        id = single_pattern_row[1]

        while single_pattern_row != "-1":
            sign = Sign(single_pattern_row[0], id, single_pattern_row[12])

            while id == sign.get_pattern_id():
                sign.add_single_row(single_pattern_row)
                single_pattern_row = next(self.reader, "-1")
                id = single_pattern_row[1]

            all_signs.append(sign)
        print(f'all_signs len: {len(all_signs)}')
        return all_signs

    def save_result(self, signs, write_filename):
        if not self.lock_write:
            writefile = open(write_filename, mode='a', newline='')
            writer = csv.writer(writefile, delimiter=',', quotechar='|')

            for j, sign in enumerate(signs):
                for i in range(sign.get_pattern_size()):
                    writer.writerow(sign.get_csv_row(i))

    def sample_shift_position(self, signs, a=0, b=0, alfa=0, beta=0):
        new_signs = []

        for i, sign in enumerate(signs):
            sign_position = sign.get_position()
            transformed_position = defaultdict(list)

            for x, y in zip(sign_position['x'], sign_position['y']):
                s = random.uniform(a, b)
                fi = random.uniform(alfa, beta)
                x_new, y_new = self.shift(x, y, s, fi)
                transformed_position['x'].append(x_new)
                transformed_position['y'].append(y_new)

            transformed_sign = copy.deepcopy(sign)
            transformed_sign.set_pattern_id(i)
            transformed_sign.set_position(transformed_position)
            new_signs.append(transformed_sign)
        return new_signs

    def sample_shift_time(self, signs):
        new_signs = []

        for i, sign in enumerate(signs):
            delta_t = sign.get_delta_t()
            new_sign_time = [delta_t[0]]

            for j in range(2, len(delta_t)):
                random_time = random.randrange(new_sign_time[j-2]+1, delta_t[j], 1)
                new_sign_time.append(random_time)

            new_sign_time.append(delta_t[-1])
            transformed_sign = copy.deepcopy(sign)
            transformed_sign.set_pattern_id(i)
            transformed_sign.set_delta_t(new_sign_time)
            new_signs.append(transformed_sign)
        return new_signs

    def shift(self, x, y, s, fi):
        x_new = float(x) + s * math.cos(fi)
        y_new = float(y) + s * math.sin(fi)
        return x_new, y_new

    def rotate_around_xyz_axis(self, signs, acc_or_gyr="acc", angle_range=0, axis="x"):
        new_signs = []

        for i, sign in enumerate(signs):
            rotated_data = defaultdict(list)
            data_dir = sign.get_acc() if acc_or_gyr=="acc" else sign.get_gyr()
            angle = random.uniform(0, angle_range)

            for x, y, z in zip(data_dir['x'], data_dir['y'], data_dir['z']):
                if axis == "x":
                    x_new = x
                    y_new = math.cos(angle)*y + math.sin(angle)*z
                    z_new = -math.sin(angle)*y + math.cos(angle)*z
                elif axis == "y":
                    x_new = math.cos(angle)*x - math.sin(angle)*z
                    y_new = y
                    z_new = math.sin(angle) * x + math.cos(angle)*z

                rotated_data['x'].append(x_new)
                rotated_data['y'].append(y_new)
                rotated_data['z'].append(z_new)

            transformed_sign = copy.deepcopy(sign)
            transformed_sign.set_pattern_id(i)

            if acc_or_gyr == "acc":
                transformed_sign.set_acc(rotated_data)
            else:
                transformed_sign.set_gyr(rotated_data)
            new_signs.append(transformed_sign)
        return new_signs

    def remove_unnecessary_samples(self, signs, delta_a=4, delta_d=0.05, delta_v=0.0009):
        new_signs = []

        for sign in signs:
            sign_position = sign.get_position()
            time = sign.get_delta_t()

            valid_sample_list = [True]
            last_valid_sample = 0

            for i in range(1, len(time)-1):
                valid_slope = self.valid_slope(sign_position, i, math.tan(delta_a*math.pi/180))
                valid_velocity = self.valid_velocity(sign_position, time, i, delta_v)
                valid_distance = self.valid_distance_2D(sign_position, i, last_valid_sample, delta_d)

                valid_sample_list.append(valid_slope or valid_velocity or valid_distance)

                if valid_slope or valid_velocity or valid_distance:
                    last_valid_sample = i

            valid_sample_list.append(True)
            new_sign = self.get_new_sign(sign, valid_sample_list)
            new_signs.append(new_sign)
        return new_signs

    def valid_slope(self, sign_position, sample_id, delta):
        p0 = [sign_position['x'][sample_id - 1], sign_position['y'][sample_id - 1]]
        p1 = [sign_position['x'][sample_id], sign_position['y'][sample_id]]
        p2 = [sign_position['x'][sample_id + 1], sign_position['y'][sample_id + 1]]

        if p1[0] == p0[0] or p2[0] == p1[0]:
            return False

        a0 = (p1[1] - p0[1]) / (p1[0] - p0[0])
        a1 = (p2[1] - p1[1]) / (p2[0] - p1[0])

        delta_a = math.fabs(a1 - a0)
        return not delta_a <= delta

    def valid_velocity(self, sign_position, time, sample_id, delta):
        d0 = self.get_distance_2D(sign_position, sample_id-1, sample_id)
        v0 = d0 / (time[sample_id] - time[sample_id-1])
        d1 = self.get_distance_2D(sign_position, sample_id, sample_id+1)

        if time[sample_id+1] - time[sample_id] != 0:
            v1 = d1 / (time[sample_id+1] - time[sample_id])
        else:
            v1 = d1 / 0.00001

        delta_v = math.fabs(v1 - v0)

        return not delta_v <= delta

    def get_distance_2D(self, sign_position, sample_id, last_valid_sample_id):
        p0 = [sign_position['x'][last_valid_sample_id], sign_position['y'][last_valid_sample_id]]
        p1 = [sign_position['x'][sample_id], sign_position['y'][sample_id]]
        distance = math.sqrt(math.pow((p1[0]-p0[0]), 2) + math.pow((p1[1]-p0[1]), 2))
        return distance

    def valid_distance_2D(self, sign_position, sample_id, last_valid_sample_id, delta_d):
        d = self.get_distance_2D(sign_position, sample_id, last_valid_sample_id)
        return not d < delta_d

    def get_new_sign(self, reference_sign, valid_sample):
        new_sign = copy.deepcopy(reference_sign)
        time = reference_sign.get_delta_t()
        position = reference_sign.get_position()
        acc = reference_sign.get_acc()
        gyr = reference_sign.get_gyr()

        new_position = defaultdict(list)
        new_delta_t = []
        new_acc = defaultdict(list)
        new_gyr = defaultdict(list)

        for i, valid in enumerate(valid_sample):
            if valid:
                new_position['x'].append(position['x'][i])
                new_position['y'].append(position['y'][i])
                new_delta_t.append(time[i])
                new_acc['x'].append(acc['x'][i])
                new_acc['y'].append(acc['y'][i])
                new_acc['z'].append(acc['z'][i])
                new_gyr['x'].append(gyr['x'][i])
                new_gyr['y'].append(gyr['y'][i])
                new_gyr['z'].append(gyr['z'][i])

        new_sign.set_position(new_position)
        new_sign.set_delta_t(new_delta_t)
        new_sign.set_gyr(new_gyr)
        new_sign.set_acc(new_acc)
        return new_sign

    def get_repeated_time(self):
        for sign in self.all_signs:
            time = dict(Counter(sign.get_delta_t()))
            for time, repeat in time.items():
                if repeat > 1:
                    print("Repeated: ", repeat)


if __name__ == "__main__":
    base_path = 'data/csv/' + SIGN + '/data_13_09_2020-' + SIGN
    filename = base_path + '-general.csv'

    data_augmentation = DataAugmentation(filename)
    signs = data_augmentation.load_all_signs()

    if AUGMENTATION_TYPE == 1:
        transformed_data = data_augmentation.sample_shift_position(signs, a=0.03, b=0.06, alfa=0, beta=2*math.pi)
        write_filename = base_path + '-shifted_pos.csv'
    elif AUGMENTATION_TYPE == 2:
        transformed_data = data_augmentation.sample_shift_time(signs)
        write_filename = base_path + '-shifted_time.csv'
    elif AUGMENTATION_TYPE == 3:
        transformed_data = data_augmentation.rotate_around_xyz_axis(signs, acc_or_gyr="gyr", angle_range=math.pi / 3, axis="y")
        transformed_data = data_augmentation.rotate_around_xyz_axis(transformed_data, acc_or_gyr="acc", angle_range=math.pi / 3, axis="y")
        write_filename = base_path + '-rotated_gyr_y_acc_y.csv'
    elif AUGMENTATION_TYPE == 4:
        transformed_data = data_augmentation.remove_unnecessary_samples(signs, delta_a=15, delta_d=60, delta_v=1.6)
        write_filename = base_path + '-removed_delta_a=15-delta_d=60-delta_v=1.6.csv'

    data_augmentation.save_result(transformed_data, write_filename)
