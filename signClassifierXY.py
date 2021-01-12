from PyQt5 import QtWidgets, uic
from sign import Sign
from collections import defaultdict

import csv
import pyqtgraph as pg
import sys

sign_id = 1

reference_sign_1 = ['166.0,724.0', '187.85599,724.7743', '238.75279,725.0', '292.48706,725.0', '350.58838,725.0', '421.60162,725.0', '507.34967,724.0663', '601.54034,721.0559', '684.815,718.06067', '752.5971,714.0905', '808.0227,713.0', '836.1239,712.0', '851.51227,713.90247', '856.0,717.8224', '843.3438,730.7326', '817.0022,759.931', '775.8371,808.98096', '727.10864,862.8103', '654.26294,920.6189', '572.6175,974.3602', '491.45306,1025.3489', '412.67572,1090.1016', '347.22037,1147.7797', '291.45752,1207.0105', '251.15765,1261.2241', '215.92416,1304.9763', '202.40915,1337.227', '202.0,1354.147', '204.57224,1360.5723', '215.8789,1363.0', '240.78859,1359.4423', '280.82486,1353.501', '342.3651,1341.0139', '416.623,1318.8977', '505.96533,1291.3448', '599.4412,1267.9336', '690.9546,1248.5741', '769.97894,1236.7826', '850.50183,1233.141', '887.0,1233.0']
reference_sign_2 = ['846.0,738.0', '828.7837,732.6959', '775.18524,728.27814', '701.02545,727.0', '625.4955,730.3293', '559.119,748.55554', '487.25793,781.2455', '415.79364,838.2063', '353.7167,910.68506', '302.60046,1000.06836', '264.1902,1074.7864', '249.7994,1152.7426', '249.73662,1227.5183', '268.5437,1290.0239', '302.91452,1343.5497', '349.51468,1387.3253', '410.4489,1416.3962', '482.2038,1422.2881', '546.8418,1417.0316', '609.4443,1397.7599', '663.02106,1376.2612', '710.37103,1344.629', '746.3811,1294.2804', '782.47675,1232.9158', '802.5807,1188.0482', '812.38385,1155.3132', '812.3085,1137.1594', '812.0,1127.3113', '804.9806,1119.9806', '800.61053,1117.6106', '798.0,1116.6829', '796.3361,1115.3362', '790.6579,1114.0', '786.69604,1115.652', '782.6792,1116.0', '776.3009,1116.6748', '761.2709,1118.6715', '727.9762,1121.0', '687.93665,1119.3492', '658.28107,1119.0', '631.99036,1118.3564', '595.1702,1118.0', '551.52026,1114.9832', '543.0,1114.0']
reference_sign_3 = ['264.0,1367.0', '266.64905,1361.9006', '278.859,1355.5059', '307.00107,1348.7058', '379.36237,1346.3594', '456.80563,1347.636', '528.08685,1351.8932', '595.272,1359.4543', '658.46826,1369.5336', '709.5812,1376.268', '751.0542,1378.0', '792.0162,1376.374', '821.8225,1373.7396', '844.74176,1368.1614', '860.76294,1359.8643', '870.13116,1350.8688', '873.0,1331.8746', '874.0,1302.4108', '870.26276,1260.7856', '867.8335,1207.5853', '869.20264,1163.1763', '872.6005,1120.3887', '879.3399,1070.2057', '886.6193,1014.8862', '895.8127,964.49915', '904.6324,912.94104', '911.74554,868.7811', '916.0,826.44446', '913.43176,794.0447', '911.45105,768.51044', '912.0,754.28217', '911.4465,748.89294', '909.42847,748.0', '902.092,748.0', '885.58905,750.14014', '853.3585,758.83575', '813.10675,768.36346', '768.8141,779.76953', '713.1759,790.228', '641.57214,796.0', '557.07477,793.9337', '481.4927,787.99927', '423.93628,782.4265', '378.95853,775.41455', '344.97675,773.0', '325.80832,771.93616', '317.9431,771.52844', '315.0,773.0702', '314.0,779.61755', '314.47598,796.81213', '309.48477,829.09143', '300.93384,869.397', '292.4791,920.6742', '286.39008,977.09924', '284.51346,1026.3234', '286.01004,1073.6053', '294.20184,1112.6055', '310.65668,1143.7263', '328.76663,1161.3367', '354.21207,1168.0', '391.99634,1162.2737', '439.27545,1146.9408', '493.4707,1128.1696', '559.99677,1109.9666', '618.3119,1096.8014', '666.4751,1087.6464', '707.7444,1085.9111', '717.0,1087.0']

if sign_id == 1:
    reference_sign = reference_sign_1
elif sign_id == 2:
    reference_sign = reference_sign_2
elif sign_id == 3:
    reference_sign = reference_sign_3

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('widgets/WidgetXY.ui', self)
        self.lock = True
        self.i = -1
        self.reader = None
        self.writer = None
        self.pattern = None
        self.reference_sign = defaultdict(list)
        self.open_file_handles()
        self.load_reference_sign()
        self.single_pattern_row = next(self.reader)
        self.next_pattern()
        self.show()

        self.graphWidget.setBackground('w')

        self.incorrectButton.clicked.connect(self.invalid_sign)
        self.correctButton.clicked.connect(self.valid_sign)

    def open_file_handles(self):
        readfilename = 'data/csv/sign_' + str(sign_id) + '/data_13_09_2020-sign_' + str(sign_id) + '.csv'
        writefilename = 'data/csv/sign_' + str(sign_id) + '/data_13_09_2020-sign_' + str(sign_id) + '-classified_xy.csv'

        readfile = open(readfilename, mode='r', newline='')
        self.reader = csv.reader(readfile)
        next(self.reader)  # Skip the header

        writefile = open(writefilename, mode='a', newline='')
        self.writer = csv.writer(writefile, delimiter=',', quotechar='|')
        self.writer.writerow(['user', 'pattern_id', 'pos_x', 'pos_y', 'order_no', 'time', 'acc_x', 'acc_y', 'acc_z',
                              'gyr_x', 'gyr_y', 'gyr_z',  'valid_sign'])

    def load_sign(self):
        id = self.single_pattern_row[1]
        sign = Sign(self.single_pattern_row[0], id, self.single_pattern_row[12])

        while id == sign.get_pattern_id():
            sign.add_single_row(self.single_pattern_row)
            self.single_pattern_row = next(self.reader, "-1")
            id = self.single_pattern_row[1]
        return sign

    def valid_sign(self):
        self.save_result()
        self.next_pattern()

    def invalid_sign(self):
        self.pattern.set_valid_state(False)
        self.save_result()
        self.next_pattern()

    def next_pattern(self):
        if self.single_pattern_row == "-1":
            self.lock = True
            print("Koniec znakow")
            return

        self.pattern = self.load_sign()

        if self.pattern.get_user() == 'True' and self.pattern.get_valid_sign() == 'True':
            penSign = pg.mkPen(color=(0, 255, 0), width=20)
            penPatternSign = pg.mkPen(color=(0, 0, 255), width=2)

            self.graphWidget.clear()
            self.graphWidget.plot(self.reference_sign['x'], self.reference_sign['y'], pen=penSign)
            self.graphWidget.plot(self.pattern.get_position()['x'], self.pattern.get_position()['y'], pen=penPatternSign)
        else:
            self.invalid_sign()

    def save_result(self):
        if not self.lock:
            for i in range(self.pattern.get_pattern_size()):
                self.writer.writerow(self.pattern.get_csv_row(i))

    def load_reference_sign(self):
        for position in reference_sign:
            position = position.split(",")
            self.reference_sign['x'].append(float(position[0]))
            self.reference_sign['y'].append(float(position[1]))

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
