# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sender_window.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QMessageBox,QPlainTextEdit
from sender import Sender
from PyQt5.QtGui import QIntValidator
import threading
from datetime import datetime 
from queue import Queue
import socket

class Ui_MainWindow(QWidget):

    def setupUi(self, MainWindow):
        self.__sender = Sender(Sender.DEFAULT_IP, Sender.DEFAULT_PORT)
        self.__socket_created = False
        self.__sender.log_message_signal.connect(self.write_in_log)
        self.__sender.file_sent_signal.connect(self.enable_components)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 560)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_slider = QtWidgets.QSlider(self.centralwidget)
        self.window_slider.setGeometry(QtCore.QRect(170, 140, 341, 22))
        self.window_slider.setOrientation(QtCore.Qt.Horizontal)
        self.window_slider.setObjectName("window_slider")
        self.window_size_label = QtWidgets.QLabel(self.centralwidget)
        self.window_size_label.setGeometry(QtCore.QRect(10, 140, 151, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.window_size_label.setFont(font)
        self.window_size_label.setObjectName("window_size_label")
        self.timeout_label = QtWidgets.QLabel(self.centralwidget)
        self.timeout_label.setGeometry(QtCore.QRect(10, 180, 131, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.timeout_label.setFont(font)
        self.timeout_label.setObjectName("timeout_label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(880, 20, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.timeout_text_field = QtWidgets.QLineEdit(self.centralwidget)
        self.timeout_text_field.setGeometry(QtCore.QRect(170, 180, 113, 22))
        self.timeout_text_field.setObjectName("timeout_text_field")
        self.set_timeout_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_timeout_button.setGeometry(QtCore.QRect(300, 180, 93, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_timeout_button.setFont(font)
        self.set_timeout_button.setObjectName("set_timeout_button")
        self.log_label = QtWidgets.QLabel(self.centralwidget)
        self.log_label.setGeometry(QtCore.QRect(10, 290, 131, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.log_label.setFont(font)
        self.log_label.setObjectName("log_label")

        self.log_text_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.log_text_edit.setGeometry(QtCore.QRect(10, 320, 731, 191))
        self.log_text_edit.setObjectName("logg_text_edit")

        self.test_connection_button = QtWidgets.QPushButton(self.centralwidget)
        self.test_connection_button.setGeometry(QtCore.QRect(450, 60, 150, 50))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.test_connection_button.setFont(font)
        self.test_connection_button.setObjectName("test_connection_button")
        self.test_connection_button.clicked.connect(self.check_connection_pressed)

        self.path_text_field = QtWidgets.QLineEdit(self.centralwidget)
        self.path_text_field.setGeometry(QtCore.QRect(10, 10, 591, 22))
        self.path_text_field.setObjectName("path_text_field")
        self.file_select_button = QtWidgets.QPushButton(self.centralwidget)
        self.file_select_button.setGeometry(QtCore.QRect(610, 10, 131, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.file_select_button.setFont(font)
        self.file_select_button.setObjectName("file_select_button")
        self.IP_label = QtWidgets.QLabel(self.centralwidget)
        self.IP_label.setGeometry(QtCore.QRect(10, 50, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IP_label.setFont(font)
        self.IP_label.setObjectName("IP_label")
        self.ip_text_field_1 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_1.setGeometry(QtCore.QRect(60, 50, 31, 22))
        self.ip_text_field_1.setText("")
        self.ip_text_field_1.setObjectName("ip_text_field_1")
        self.ip_text_field_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_4.setGeometry(QtCore.QRect(240, 50, 31, 22))
        self.ip_text_field_4.setText("")
        self.ip_text_field_4.setObjectName("ip_text_field_4")
        self.ip_text_field_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_2.setGeometry(QtCore.QRect(120, 50, 31, 22))
        self.ip_text_field_2.setText("")
        self.ip_text_field_2.setObjectName("ip_text_field_2")
        self.ip_text_field_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_3.setGeometry(QtCore.QRect(180, 50, 31, 22))
        self.ip_text_field_3.setText("")
        self.ip_text_field_3.setObjectName("ip_text_field_3")
        self.ip_label_1 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_1.setGeometry(QtCore.QRect(100, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_1.setFont(font)
        self.ip_label_1.setObjectName("ip_label_1")
        self.ip_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_2.setGeometry(QtCore.QRect(160, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_2.setFont(font)
        self.ip_label_2.setObjectName("ip_label_2")
        self.ip_label_3 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_3.setGeometry(QtCore.QRect(220, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_3.setFont(font)
        self.ip_label_3.setObjectName("ip_label_3")
        self.set_IP_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_IP_button.setGeometry(QtCore.QRect(300, 50, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_IP_button.setFont(font)
        self.set_IP_button.setObjectName("set_IP_button")
        self.port_Label = QtWidgets.QLabel(self.centralwidget)
        self.port_Label.setGeometry(QtCore.QRect(10, 100, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.port_Label.setFont(font)
        self.port_Label.setObjectName("port_Label")
        self.port_text_field = QtWidgets.QLineEdit(self.centralwidget)
        self.port_text_field.setGeometry(QtCore.QRect(60, 100, 61, 22))
        self.port_text_field.setObjectName("port_text_field")
        self.set_port_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_port_button.setGeometry(QtCore.QRect(300, 100, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_port_button.setFont(font)
        self.set_port_button.setObjectName("set_port_button")
        self.start_sender_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_sender_button.setGeometry(QtCore.QRect(630, 230, 111, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.start_sender_button.setFont(font)
        self.start_sender_button.setObjectName("start_sender_button")
        self.window_size_value_label = QtWidgets.QLabel(self.centralwidget)
        self.window_size_value_label.setGeometry(QtCore.QRect(530, 140, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.window_size_value_label.setFont(font)
        self.window_size_value_label.setText("")
        self.window_size_value_label.setObjectName("window_size_value_label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 750, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.window_slider.valueChanged.connect(self.on_slider)
        self.window_slider.setSingleStep(10)
        self.window_slider.setTickInterval(20)
        self.window_slider.setRange(10,100)
        self.window_slider.setPageStep(10)

        self.set_timeout_button.clicked.connect(self.setTimeout)
        self.file_select_button.clicked.connect(self.openFileNamesDialog)
        self.set_IP_button.clicked.connect(self.setIP)
        self.set_port_button.clicked.connect(self.setPort)

        self.ip_text_field_1.setValidator(QIntValidator(0, 255))
        self.ip_text_field_2.setValidator(QIntValidator(0, 255))
        self.ip_text_field_3.setValidator(QIntValidator(0, 255))
        self.ip_text_field_4.setValidator(QIntValidator(0, 255))
        self.port_text_field.setValidator(QIntValidator(0, 65535))

        self.start_sender_button.clicked.connect(self.start_sender)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.window_size_label.setText(_translate("MainWindow", "Dimensiune fereastra"))
        self.timeout_label.setText(_translate("MainWindow", "Valoarea de timeout"))
        self.pushButton.setText(_translate("MainWindow", "Trimite fisier"))
        self.set_timeout_button.setText(_translate("MainWindow", "Seteaza"))
        self.log_label.setText(_translate("MainWindow", "Log-ul transferului"))
        self.file_select_button.setText(_translate("MainWindow", "Selecteaza fisier..."))
        self.IP_label.setText(_translate("MainWindow", "IP"))
        self.ip_label_1.setText(_translate("MainWindow", "."))
        self.ip_label_2.setText(_translate("MainWindow", "."))
        self.ip_label_3.setText(_translate("MainWindow", "."))
        self.set_IP_button.setText(_translate("MainWindow", "Seteaza IP"))
        self.port_Label.setText(_translate("MainWindow", "Port"))
        self.set_port_button.setText(_translate("MainWindow", "Seteaza port"))
        self.start_sender_button.setText(_translate("MainWindow", "Start Sender"))
        self.test_connection_button.setText(_translate("MainWindow", "Testeaza conexiunea"))

        self.set_ip_in_text_field(self.__sender.get_sender_ip())

    def set_ip_in_text_field(self, given_ip: str):
        self.ip_text_field_1.setText(given_ip.split(".")[0])
        self.ip_text_field_2.setText(given_ip.split(".")[1])
        self.ip_text_field_3.setText(given_ip.split(".")[2])
        self.ip_text_field_4.setText(given_ip.split(".")[3])

    def get_ip_from_text_field(self):
        ip1 = self.ip_text_field_1.text()
        ip2 = self.ip_text_field_2.text()
        ip3 = self.ip_text_field_3.text()
        ip4 = self.ip_text_field_4.text()

        return ip1 + "." + ip2 + "." + ip3 + "." + ip4

    def on_slider(self, value):
        self.window_size_value_label.setText(str(value))
        self.__sender.set_window_size(value)

    def setTimeout(self):
        pass

    def setPort(self):
        port = self.port_text_field.text()
        if(int(port) > 65535):
            QMessageBox.about(self, "Eroare!", "Valoarea " + port + " este invalida! ( 0 - 255)" )
            return

    def setIP(self):
        ip1 = self.ip_text_field_1.text()
        ip2 = self.ip_text_field_2.text()
        ip3 = self.ip_text_field_3.text()
        ip4 = self.ip_text_field_4.text()

        if(int(ip1) > 255):
             QMessageBox.about(self, "Eroare!", "Valoarea " + ip1 + " este invalida! ( 0 - 255)" )
             return

        if(int(ip2) > 255):
             QMessageBox.about(self, "Eroare!", "Valoarea " + ip2 + " este invalida! ( 0 - 255)" )
             return

        if(int(ip3) > 255):
             QMessageBox.about(self, "Eroare!", "Valoarea " + ip3 + " este invalida! ( 0 - 255)" )
             return

        if(int(ip4) > 255):
             QMessageBox.about(self, "Eroare!", "Valoarea " + ip4 + " este invalida! ( 0 - 255)" )
             return

        self.__sender.set_ip(ip1 + "." + ip2 + "." + ip3 + "." + ip4)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        self.path_text_field.setText(str(files)[2:-2])
        self.__sender.set_file_path(str(files)[2:-2])

    def start_sender(self):
        try:
            if self.path_text_field.text() == "":
                QMessageBox.about(self, "Eroare!", "Trebuie sa alegeti un fisier de trimis!" )  
                return

            if self.__socket_created == False:
                self.__sender.create_socket("AF_INET", "SOCK_DGRAM")
                self.__socket_created == True
                
            thread_sender = threading.Thread(target=self.__sender.start_sender)
            thread_sender.start()

            self.window_slider.setEnabled(False)
            self.set_IP_button.setEnabled(False)
            self.set_port_button.setEnabled(False)
            self.set_timeout_button.setEnabled(False)
            self.start_sender_button.setEnabled(False)

            if self.get_ip_from_text_field != "127.0.0.1":
                host_name = socket.gethostname() 
                host_ip = socket.gethostbyname(host_name) 
                self.__sender.set_ip(host_ip)
            else:
                print("e ok")

        except Exception as e:
            QMessageBox.about(self, "Eroare!", "Eroare la pornirea sender-ului!" )  
            QMessageBox.about(self, "Eroare!", str(e) )  


    def write_in_log(self, message):
        self.log_text_edit.append(message)
    
    def enable_components(self, file_sent):
        if file_sent == True:
            self.window_slider.setEnabled(True)
            self.set_IP_button.setEnabled(True)
            self.set_port_button.setEnabled(True)
            self.set_timeout_button.setEnabled(True)
            self.start_sender_button.setEnabled(True)

    def check_connection_pressed(self):
        self.__sender.check_connection()
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


