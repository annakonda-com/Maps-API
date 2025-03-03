import os
import sys

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QRadioButton, QLineEdit, QPushButton

SCREEN_SIZE = [600, 600]
STEP = [5, 2, 1, 0.5, 0.05]


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class ShowGeo(QWidget):
    def __init__(self):
        super().__init__()
        self.ll = [37.530887, 55.703118]
        self.z = 17
        self.not_ness = ''
        self.theme = "light"
        self.initUI()
        self.show_image()
        self.search.clicked.connect(self.search_clckd)

    def search_clckd(self):
        self.ll = self.find_by_geocoder(self.input.text())
        self.not_ness = f"{','.join(list(map(str, self.ll)))},pm2pnl"
        self.show_image()

    def find_by_geocoder(self, lost):
        server_address = 'https://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocoder_request = f'{server_address}apikey={api_key}&geocode={lost}&lang=ru_RU&format=json'
        response = requests.get(geocoder_request)
        if response:
            json_response = response.json()
            result = list(
                map(float, json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"][
                    "pos"].split()))
        else:
            print(f"Ошибка выполнения запроса при поиске {lost}:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        return result

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

        self.radio_btn = QRadioButton(self)
        self.radio_btn.setText("Тёмная тема")
        self.radio_btn.move(30, 470)
        self.radio_btn.toggled.connect(self.dark_mode)

    def dark_mode(self):
        if self.radio_btn.isChecked():
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
