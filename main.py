import os
import sys

import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

SCREEN_SIZE = [600, 450]


class ShowGeo(QWidget):
    def __init__(self):
        super().__init__()
        self.ll = [37.530887, 55.703118]
        self.z = 17
        self.initUI()
        self.show_image()

    def getImage(self):
        apikey = '4dbe104a-d5c7-4d20-bb68-3ae6ac4cae00'
        map_params = {
            "ll": ",".join([str(self.ll[0]), str(self.ll[1])]),
            "apikey": apikey,
            'z': self.z
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

    def show_image(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowGeo()
    ex.show()
    sys.exit(app.exec())
