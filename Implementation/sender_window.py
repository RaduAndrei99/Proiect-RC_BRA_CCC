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

class SenderGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.__sender = Sender(Sender.DEFAULT_IP, Sender.DEFAULT_PORT)

        self.setupUi(self)
        
        self.__socket_created = False
        self.__sender.log_message_signal.connect(self.write_in_log)
        self.__sender.file_sent_signal.connect(self.enable_components)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(750, 560)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.window_slider = QtWidgets.QSlider(self.centralwidget)
        self.window_slider.setGeometry(QtCore.QRect(260, 140, 271, 22))
        self.window_slider.setOrientation(QtCore.Qt.Horizontal)
        self.window_slider.setObjectName("window_slider")
        self.window_size_label = QtWidgets.QLabel(self.centralwidget)
        self.window_size_label.setGeometry(QtCore.QRect(10, 140, 211, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.window_size_label.setFont(font)
        self.window_size_label.setObjectName("window_size_label")
        self.timeout_label = QtWidgets.QLabel(self.centralwidget)
        self.timeout_label.setGeometry(QtCore.QRect(10, 220, 171, 16))
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

        self.test_connection_button = QtWidgets.QPushButton(self.centralwidget)
        self.test_connection_button.setGeometry(QtCore.QRect(590, 60, 150, 50))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.test_connection_button.setFont(font)
        self.test_connection_button.setObjectName("test_connection_button")
        self.test_connection_button.clicked.connect(self.check_connection_pressed)

        self.timeout_text_field = QtWidgets.QLineEdit(self.centralwidget)
        self.timeout_text_field.setGeometry(QtCore.QRect(180, 220, 113, 22))
        self.timeout_text_field.setObjectName("timeout_text_field")
        self.set_timeout_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_timeout_button.setGeometry(QtCore.QRect(310, 220, 131, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_timeout_button.setFont(font)
        self.set_timeout_button.setObjectName("set_timeout_button")
        self.log_label = QtWidgets.QLabel(self.centralwidget)
        self.log_label.setGeometry(QtCore.QRect(10, 260, 131, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.log_label.setFont(font)
        self.log_label.setObjectName("log_label")
        self.log_text_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.log_text_edit.setGeometry(QtCore.QRect(10, 320, 731, 231))
        self.log_text_edit.setObjectName("log_text_edit")
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
        self.IP_label.setGeometry(QtCore.QRect(10, 50, 101, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.IP_label.setFont(font)
        self.IP_label.setObjectName("IP_label")
        self.ip_text_field_1 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_1.setGeometry(QtCore.QRect(140, 50, 31, 22))
        self.ip_text_field_1.setText("")
        self.ip_text_field_1.setObjectName("ip_text_field_1")
        self.ip_text_field_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_4.setGeometry(QtCore.QRect(320, 50, 31, 22))
        self.ip_text_field_4.setText("")
        self.ip_text_field_4.setObjectName("ip_text_field_4")
        self.ip_text_field_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_2.setGeometry(QtCore.QRect(200, 50, 31, 22))
        self.ip_text_field_2.setText("")
        self.ip_text_field_2.setObjectName("ip_text_field_2")
        self.ip_text_field_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.ip_text_field_3.setGeometry(QtCore.QRect(260, 50, 31, 22))
        self.ip_text_field_3.setText("")
        self.ip_text_field_3.setObjectName("ip_text_field_3")
        self.ip_label_1 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_1.setGeometry(QtCore.QRect(180, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_1.setFont(font)
        self.ip_label_1.setObjectName("ip_label_1")
        self.ip_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_2.setGeometry(QtCore.QRect(240, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_2.setFont(font)
        self.ip_label_2.setObjectName("ip_label_2")
        self.ip_label_3 = QtWidgets.QLabel(self.centralwidget)
        self.ip_label_3.setGeometry(QtCore.QRect(300, 50, 16, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.ip_label_3.setFont(font)
        self.ip_label_3.setObjectName("ip_label_3")
        self.set_IP_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_IP_button.setGeometry(QtCore.QRect(380, 50, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_IP_button.setFont(font)
        self.set_IP_button.setObjectName("set_IP_button")
        self.port_Label = QtWidgets.QLabel(self.centralwidget)
        self.port_Label.setGeometry(QtCore.QRect(10, 100, 111, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.port_Label.setFont(font)
        self.port_Label.setObjectName("port_Label")
        self.port_text_field = QtWidgets.QLineEdit(self.centralwidget)
        self.port_text_field.setGeometry(QtCore.QRect(140, 100, 61, 22))
        self.port_text_field.setObjectName("port_text_field")
        self.set_port_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_port_button.setGeometry(QtCore.QRect(380, 100, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.set_port_button.setFont(font)
        self.set_port_button.setObjectName("set_port_button")
        self.start_sender_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_sender_button.setGeometry(QtCore.QRect(630, 190, 111, 71))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.start_sender_button.setFont(font)
        self.start_sender_button.setObjectName("start_sender_button")
        self.window_size_value_label = QtWidgets.QLabel(self.centralwidget)
        self.window_size_value_label.setGeometry(QtCore.QRect(550, 140, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.window_size_value_label.setFont(font)
        self.window_size_value_label.setText("")
        self.window_size_value_label.setObjectName("window_size_value_label")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 180, 201, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.packet_slider = QtWidgets.QSlider(self.centralwidget)
        self.packet_slider.setGeometry(QtCore.QRect(260, 180, 271, 22))
        self.packet_slider.setOrientation(QtCore.Qt.Horizontal)
        self.packet_slider.setObjectName("packet_slider")
        self.packet_size_value_label = QtWidgets.QLabel(self.centralwidget)
        self.packet_size_value_label.setGeometry(QtCore.QRect(550, 180, 55, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.packet_size_value_label.setFont(font)
        self.packet_size_value_label.setText("")
        self.packet_size_value_label.setObjectName("packet_size_value_label")
        #MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.window_slider.valueChanged.connect(self.on_window_slider)
        self.window_slider.setSingleStep(10)
        self.window_slider.setTickInterval(10)
        self.window_slider.setRange(10,100)
        self.window_slider.setPageStep(10)

        self.packet_slider.valueChanged.connect(self.on_packet_slider)
        self.packet_slider.setSingleStep(64)
        self.packet_slider.setTickInterval(10)
        self.packet_slider.setRange(64,2**16 - 1 - 4  )
        self.packet_slider.setPageStep(64)

        self.set_timeout_button.clicked.connect(self.setTimeout)
        self.file_select_button.clicked.connect(self.openFileNamesDialog)
        self.set_IP_button.clicked.connect(self.setIP)
        self.set_port_button.clicked.connect(self.setPort)

        self.ip_text_field_1.setValidator(QIntValidator(0, 255))
        self.ip_text_field_2.setValidator(QIntValidator(0, 255))
        self.ip_text_field_3.setValidator(QIntValidator(0, 255))
        self.ip_text_field_4.setValidator(QIntValidator(0, 255))

        self.timeout_text_field.setValidator(QIntValidator(10, 10000))


        self.start_sender_button.clicked.connect(self.start_sender)

        self.timeout_text_field.setText("200")


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.window_size_label.setText(_translate("MainWindow", "Dimensiune fereastra (pachete)"))
        self.timeout_label.setText(_translate("MainWindow", "Valoarea de timeout (ms)"))
        self.pushButton.setText(_translate("MainWindow", "Trimite fisier"))
        self.set_timeout_button.setText(_translate("MainWindow", "Seteaza valoare"))
        self.log_label.setText(_translate("MainWindow", "Log-ul transferului"))
        self.file_select_button.setText(_translate("MainWindow", "Selecteaza fisier..."))
        self.IP_label.setText(_translate("MainWindow", "IP-ul destinatie"))
        self.ip_label_1.setText(_translate("MainWindow", "."))
        self.ip_label_2.setText(_translate("MainWindow", "."))
        self.ip_label_3.setText(_translate("MainWindow", "."))
        self.set_IP_button.setText(_translate("MainWindow", "Seteaza IP"))
        self.port_Label.setText(_translate("MainWindow", "Portul destinatie"))
        self.set_port_button.setText(_translate("MainWindow", "Seteaza port"))
        self.start_sender_button.setText(_translate("MainWindow", "Start Sender"))
        self.label.setText(_translate("MainWindow", "Dimensiunea pachet (octeti)"))
        self.test_connection_button.setText(_translate("MainWindow", "Testeaza conexiunea"))

        self.set_ip_in_text_field(self.__sender.get_receiver_ip())
        self.port_text_field.setText(str(self.__sender.get_receiver_port()))

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

    def on_window_slider(self, value):
        self.window_size_value_label.setText(str(value))
        self.__sender.set_window_size(value)
        self.write_in_log("S-a setat dimensiunea ferestrei la " + str(value) + " pachete.")



    def on_packet_slider(self, value):
        self.packet_size_value_label.setText(str(value))
        self.__sender.set_packet_data_size(value)
        self.write_in_log("S-a setat dimensiunea campului de date din pachet la " + str(value) + " de octeti.")
        self.write_in_log("Dimensiunea unui pachet intreg: " + str(value + 4))


    def setTimeout(self):
        timeout = self.timeout_text_field.text()
        self.__sender.set_timeout(int(timeout) / 1000)
        self.write_in_log("S-a setat valoarea timeout-ului la " + str(timeout) + " milisecunde.")


    def setPort(self):
        port = self.port_text_field.text()
        if(int(port) > 65535):
            QMessageBox.about(self, "Eroare!", "Valoarea " + port + " este invalida! ( 0 - 65535)" )
            return
        else:
            self.__sender.set_receiver_port(int(port))
        self.write_in_log("S-a setat portul pe valoarea " + str(port) + ".")


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

        self.__sender.set_receiver_ip(ip1 + "." + ip2 + "." + ip3 + "." + ip4)
        if(ip1 + "." + ip2 + "." + ip3 + "." + ip4 != Sender.DEFAULT_RECEIVER_IP):
            self.__sender.set_local_ip_address()
        else:
            self.__sender.set_loopback_ip_address()
        self.write_in_log("S-a setat IP-ul cu adresa "  + ip1 + "." + ip2 + "." + ip3 + "." + ip4)


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

            self.disable_components()

            if self.get_ip_from_text_field() != "127.0.0.1":
                self.__sender.set_local_ip_address()
            else:
                self.__sender.set_loopback_ip_address()


            self.__sender.create_socket("AF_INET", "SOCK_DGRAM")

                
            self.__thread_sender = threading.Thread(target=self.__sender.start_sender)
            self.__thread_sender.start()


        except Exception as e:
            QMessageBox.about(self, "Eroare!", "Eroare la pornirea sender-ului!" )  
            QMessageBox.about(self, "Eroare!", str(e) )  


    def write_in_log(self, message):
        self.log_text_edit.append("[" + str(datetime.now().time()) + "]" + " " + message)
    
    def disable_components(self):
        self.window_slider.setEnabled(False)
        self.set_IP_button.setEnabled(False)
        self.set_port_button.setEnabled(False)
        self.set_timeout_button.setEnabled(False)
        self.start_sender_button.setEnabled(False)          
        self.packet_slider.setEnabled(False)
        self.test_connection_button.setEnabled(False)
        self.file_select_button.setEnabled(False)


    def enable_components(self, file_sent):
        if file_sent == True:
            self.window_slider.setEnabled(True)
            self.set_IP_button.setEnabled(True)
            self.set_port_button.setEnabled(True)
            self.set_timeout_button.setEnabled(True)
            self.start_sender_button.setEnabled(True)
            self.packet_slider.setEnabled(True)
            self.test_connection_button.setEnabled(True)
            self.file_select_button.setEnabled(True)

    def check_connection_pressed(self):
        self.__sender.check_connection()
    
    def close_sender(self):
        if self.__sender.is_running():
            self.__sender.close_sender()
            self.__thread_sender.join()

    def closeEvent(self,event):
        msgBox = QMessageBox()
        msgBox.setStyleSheet("QLabel{min-width: 250px;}")
        msgBox.setWindowTitle("Confirmati iesirea...")
        msgBox.setInformativeText("Sunteti sigur ca doriti sa iesiti?\n")
        msgBox.addButton(QtWidgets.QPushButton('Nu'), QMessageBox.NoRole)
        msgBox.addButton(QtWidgets.QPushButton('Da'), QMessageBox.YesRole)
        ret_val = msgBox.exec_()

        if ret_val == 1:
            event.accept()
            self.close_sender()
        else:
            event.ignore()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sender_window = SenderGUI()
    sender_window.setWindowTitle("Sender Window")
    #ui = SenderGUI()
    #ui.setupUi(MainWindow)
    sender_window.show()
    sys.exit(app.exec_())