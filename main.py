import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QRadioButton, QLineEdit, QPushButton, QCheckBox

SCREEN_SIZE = [600, 600]
STEP = [5, 2, 1, 0.5, 0.05]


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


class ShowGeo(QWidget):
    def __init__(self):
        super().__init__()
        self.ll = [37.530887, 55.703118]
        self.z = 17
        self.not_ness = ''
        self.theme = "light"
        self.initUI()
        self.show_image()
        self.index = False
        self.postal_index = ""
        self.search.clicked.connect(self.search_clckd)
        self.reset.clicked.connect(self.reset_clckd)

    def reset_clckd(self):
        self.not_ness = ''
        self.label1.setText("")
        self.postal_index = ""
        self.show_image()

    def search_clckd(self):
        response = self.find_by_geocoder(self.input.text())
        self.ll = self.find_pos(response)
        self.not_ness = f"{','.join(list(map(str, self.ll)))},pm2pnl"
        self.postal_index = self.adress_index(response)
        self.show_image()
        if not self.index:
            self.label1.setText(self.adress(response))
        else:
            self.label1.setText(self.adress(response) + " " + self.postal_index)

    def find_pos(self, json_response):
        return list(
            map(float, json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                "pos"].split()))

    def adress(self, json_response):
        return json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"][
            "text"]

    def adress_index(self, json_response):
        try:
            return \
                json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
                    "GeocoderMetaData"]["Address"]["postal_code"]
        except KeyError:
            return ""

    def find_by_geocoder(self, lost):
        server_address = 'https://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocoder_request = f'{server_address}apikey={api_key}&geocode={lost}&lang=ru_RU&format=json'
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
        else:
            print(f"Ошибка выполнения запроса при поиске {lost}:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return json_response

    def getImage(self):
        apikey = '4dbe104a-d5c7-4d20-bb68-3ae6ac4cae00'
        map_params = {
            "ll": ",".join([str(self.ll[0]), str(self.ll[1])]),
            "apikey": apikey,
            'z': self.z,
            'theme': self.theme,
            'pt': self.not_ness
        }
        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

        self.input = QLineEdit(self)
        self.input.resize(500, 30)
        self.input.move(10, 500)

        self.search = QPushButton(self)
        self.search.setText("Поиск")
        self.search.move(510, 500)
        self.radio_btn1 = QCheckBox(self)
        self.radio_btn1.setText("Тёмная тема")
        self.radio_btn1.move(30, 470)
        self.radio_btn1.stateChanged.connect(self.dark_mode)

        self.radio_btn2 = QCheckBox(self)
        self.radio_btn2.setText("Приписывать почтовый индекс")
        self.radio_btn2.move(130, 470)
        self.radio_btn2.stateChanged.connect(self.index)

        self.reset = QPushButton(self)
        self.reset.setText("Сброс поискового результата")
        self.reset.move(330, 470)

        self.label = QLabel(self)
        self.label.setText("Адрес найденного объекта:")
        self.label.move(15, 540)

        self.label1 = QLabel(self)
        self.label1.resize(400, 20)
        self.label1.move(180, 540)

    def index(self):
        if self.radio_btn2.isChecked():
            self.index = True
            self.label1.setText(self.label1.text() + " " + self.postal_index)
        else:
            if self.postal_index != "":
                self.label1.setText(" ".join(self.label1.text().split()[:-1]))
            self.index = False

    def dark_mode(self):
        if self.radio_btn1.isChecked():
            self.theme = "dark"
            self.show_image()
        else:
            self.theme = "light"
            self.show_image()

    def show_image(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.z += 1
            self.z = min(self.z, 21)
            self.show_image()
        if event.key() == Qt.Key.Key_PageDown:
            self.z -= 1
            self.z = max(self.z, 0)
            self.show_image()
        if event.key() == Qt.Key.Key_Left:
            k = STEP[self.z // len(STEP)]
            if -180 <= self.ll[0] - k <= 180:
                self.ll[0] -= k
            self.show_image()
        if event.key() == Qt.Key.Key_Right:
            k = STEP[self.z // len(STEP)]
            if -180 <= self.ll[0] + k <= 180:
                self.ll[0] += k
            self.show_image()
        if event.key() == Qt.Key.Key_Up:
            k = STEP[self.z // len(STEP)]
            if -90 <= self.ll[1] + k <= 90:
                self.ll[1] += k
            self.show_image()
        if event.key() == Qt.Key.Key_Down:
            k = STEP[self.z // len(STEP)]
            if -90 <= self.ll[1] - k <= 90:
                self.ll[1] -= k
            self.show_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowGeo()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
