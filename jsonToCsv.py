import csv
import json

SIGN_ID = 1
INPUT_FILE_PATH = 'data/json/data_13_09_2020.json'
OUTPUT_FILE_PATH = 'data/csv/sign_' + str(SIGN_ID) + '/data_13_09_2020-sign_' + str(SIGN_ID) + '.csv'


class SingleStepData:
    def __init__(self, user, position, delta_t, acc, gyr):
        self.user = user
        self.position = position
        self.delta_t = delta_t
        self.acc = acc
        self.gyr = gyr


class Sign:
    def __init__(self, sign_id):
        self.sign_id = sign_id
        self.data_list = []

    def add_new_step_data(self, sign_point):
        self.data_list.append(sign_point)

    def get_data(self):
        return self.data_list


class JsonToCsvConverter:
    def open_file(self, input_file_path):
        with open(input_file_path) as json_file:
            data = json.load(json_file)
        return data

    def parse_json(self, data, sign_id):
        signs_list = []

        if sign_id in data['signs'].keys():
            owner_name = data['patternSigns'][int(sign_id)]['author']

            sign = Sign(sign_id)

            for user_name in data['signs'][sign_id].keys():
                # next sign points
                for point_id in data['signs'][sign_id][user_name].keys():
                    single_point_data = data['signs'][sign_id][user_name][point_id]
                    data_list = single_point_data.split(",")
                    is_valid = True

                    sign_list = []
                    is_author = True if user_name == owner_name else False

                    # skip sample that is too short
                    if len(data_list) < 180:
                        is_valid = False

                    # assign split data
                    for i in range(0, len(data_list), 9):
                        position = [float(data_list[i]), float(data_list[i + 1])]
                        delta_t = data_list[i + 2]
                        acc = [data_list[i + 3], data_list[i + 4], data_list[i + 5]]
                        gyr = [data_list[i + 6], data_list[i + 7], data_list[i + 8]]

                        new_step = SingleStepData(is_author, position, delta_t, acc, gyr)
                        sign_list.append(new_step)

                    if is_valid:
                        sign.add_new_step_data(sign_list)
            signs_list.append(sign)
        return signs_list

    def save_to_csv(self, signs_list, output_file_path):
        header = ["user", "pattern_id", "pos_x", "pos_y", "order_no", "time", "acc_x", "acc_y", "acc_z", "gyr_x",
                  "gyr_y", "gyr_z", "valid_sign"]

        with open(output_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=header)
            writer.writeheader()

            for pattern_id, sign_list in enumerate(signs_list[0].get_data()):
                for order_no, step in enumerate(sign_list):
                    writer.writerow({"user": step.user, "pattern_id": pattern_id,
                                          "pos_x": step.position[0], "pos_y": step.position[1],
                                          "order_no": order_no, "time": int(step.delta_t),
                                          "acc_x": step.acc[0], "acc_y": step.acc[1], "acc_z": step.acc[2],
                                          "gyr_x": step.gyr[0], "gyr_y": step.gyr[1], "gyr_z": step.gyr[2],
                                          "valid_sign": step.user})

    def get_reference_sign_coordinates(self, data, sign_id):
        print("Reference sign coordinates: ", data['patternSigns'][sign_id]['points'])


if __name__ == "__main__":
    converter = JsonToCsvConverter()
    data = converter.open_file(INPUT_FILE_PATH)
    signs_list = converter.parse_json(data, str(SIGN_ID))
    converter.save_to_csv(signs_list, OUTPUT_FILE_PATH)