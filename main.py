import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QTextBrowser
from downloader_ui import Ui_Form
import pathlib
import foxwq_sgf_downloader
import datetime
import os
import abc
import typing


class QtextBroswer_observer(foxwq_sgf_downloader.Observer, abc.ABC):

    def __init__(self, textBroswer: QTextBrowser, downloader: foxwq_sgf_downloader.Downloader):
        self.__textBroswer = textBroswer
        self.__downloader: downloader = downloader

    def update(self) -> typing.NoReturn:
        self.__textBroswer.append(self.__downloader.get_state())
        QApplication.processEvents()


class Window(QWidget):

    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()       
        self.ui.setupUi(self)
        self.ui.dateEdit.setDate(datetime.date.today())
        self.ui.dateEdit_2.setDate(datetime.date.today())
        self.ui.pushButton_2.clicked.connect(self.open_folder)
        self.ui.pushButton.clicked.connect(self.download)
        self.show()

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "請選擇一個資料夾")
        if folder_path:
            path = pathlib.Path(folder_path)
            self.ui.lineEdit.setText(str(path))

    def download(self):
        self.ui.textBrowser.clear()
        self.ui.pushButton.setText("下載中")
        self.ui.pushButton.setEnabled(False)
        QApplication.processEvents()
        start_date = self.ui.dateEdit.date().toPyDate()
        end_date = self.ui.dateEdit_2.date().toPyDate()
        dir_path = self.ui.lineEdit.text()
        match self.ui.comboBox.currentIndex():
            case 0:
                kifu_type = "5"
            case 1:
                kifu_type = "2"
            case 2:
                kifu_type = "6"

        downloader = foxwq_sgf_downloader.Downloader(start_date, end_date, dir_path, kifu_type)
        textBroswer_observer = QtextBroswer_observer(self.ui.textBrowser, downloader)
        downloader.append_observer(textBroswer_observer)
        downloader.run()

        done_message_box = QMessageBox(self)
        done_message_box.information(self, "下載完成 !", "下載完成 !")
        self.ui.pushButton.setText("開始下載")
        self.ui.pushButton.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())
