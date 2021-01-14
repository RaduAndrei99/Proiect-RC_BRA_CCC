from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIntValidator
from packet import SWPacket
from packet import PacketType
from receiver import Receiver
from PyQt5.QtCore import pyqtSignal
import threading
import sys
import time

class ReceiverGUI(object):

    def __init__(self):
        self.receiver = None

        self.ip_address = "127.0.0.1"
        self.port = None
        self.probability = 0

        self.receiver = Receiver()
        self.receiver.signal.connect(self.write_in_log)

    def setupUi(self, ReceiverWindow):
        ReceiverWindow.setObjectName("ReceiverWindow")
        ReceiverWindow.setEnabled(True)
        ReceiverWindow.setFixedSize(750, 560)
        ReceiverWindow.setDockNestingEnabled(False)
        self.centralwidget = QtWidgets.QWidget(ReceiverWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(731, 0))
        self.centralwidget.setObjectName("centralwidget")
        self.start_stop_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_stop_button.setGeometry(QtCore.QRect(600, 130, 131, 41))
        self.start_stop_button.setObjectName("start_stop_button")
        self.start_stop_button.setCheckable(True)
        self.log_scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        self.log_scroll_area.setGeometry(QtCore.QRect(10, 220, 731, 331))
        self.log_scroll_area.setWidgetResizable(True)
        self.log_scroll_area.setObjectName("log_scroll_area")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 729, 329))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.log_plain_text = QtWidgets.QPlainTextEdit(self.scrollAreaWidgetContents)
        self.log_plain_text.setGeometry(QtCore.QRect(0, 0, 731, 340))
        self.log_plain_text.setReadOnly(True)
        self.log_plain_text.setObjectName("log_plain_text")
        self.log_scroll_area.setWidget(self.scrollAreaWidgetContents)
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 10, 731, 71))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.probability_label = QtWidgets.QLabel(self.formLayoutWidget)
        self.probability_label.setObjectName("probability_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.probability_label)
        self.probability_line_edit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.probability_line_edit.setObjectName("probability_line_edit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.probability_line_edit)
        self.progressBar = QtWidgets.QProgressBar(self.formLayoutWidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.progressBar)
        self.progres_bar_label = QtWidgets.QLabel(self.formLayoutWidget)
        self.progres_bar_label.setObjectName("progres_bar_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.progres_bar_label)
        self.loopback_radio_button = QtWidgets.QRadioButton(self.centralwidget)
        self.loopback_radio_button.setGeometry(QtCore.QRect(10, 90, 181, 31))
        self.loopback_radio_button.setChecked(True)
        self.loopback_radio_button.setObjectName("loopback_radio_button")
        self.lan_radio_button = QtWidgets.QRadioButton(self.centralwidget)
        self.lan_radio_button.setGeometry(QtCore.QRect(10, 120, 161, 31))
        self.lan_radio_button.setObjectName("lan_radio_button")
        self.loopback_line_edit_1 = QtWidgets.QLineEdit(self.centralwidget)
        self.loopback_line_edit_1.setGeometry(QtCore.QRect(200, 94, 31, 21))
        self.loopback_line_edit_1.setAlignment(QtCore.Qt.AlignCenter)
        self.loopback_line_edit_1.setReadOnly(True)
        self.loopback_line_edit_1.setObjectName("loopback_line_edit_1")
        self.dot1_label = QtWidgets.QLabel(self.centralwidget)
        self.dot1_label.setGeometry(QtCore.QRect(230, 100, 16, 17))
        self.dot1_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot1_label.setObjectName("dot1_label")
        self.loopback_line_edit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.loopback_line_edit_2.setGeometry(QtCore.QRect(240, 94, 31, 21))
        self.loopback_line_edit_2.setAlignment(QtCore.Qt.AlignCenter)
        self.loopback_line_edit_2.setReadOnly(True)
        self.loopback_line_edit_2.setObjectName("loopback_line_edit_2")
        self.loopback_line_edit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.loopback_line_edit_3.setGeometry(QtCore.QRect(280, 94, 31, 21))
        self.loopback_line_edit_3.setAlignment(QtCore.Qt.AlignCenter)
        self.loopback_line_edit_3.setReadOnly(True)
        self.loopback_line_edit_3.setObjectName("loopback_line_edit_3")
        self.dot3_label = QtWidgets.QLabel(self.centralwidget)
        self.dot3_label.setGeometry(QtCore.QRect(310, 100, 16, 17))
        self.dot3_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot3_label.setObjectName("dot3_label")
        self.dot2_label = QtWidgets.QLabel(self.centralwidget)
        self.dot2_label.setGeometry(QtCore.QRect(270, 100, 16, 17))
        self.dot2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot2_label.setObjectName("dot2_label")
        self.loopback_line_edit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.loopback_line_edit_4.setGeometry(QtCore.QRect(320, 94, 31, 21))
        self.loopback_line_edit_4.setAlignment(QtCore.Qt.AlignCenter)
        self.loopback_line_edit_4.setReadOnly(True)
        self.loopback_line_edit_4.setObjectName("loopback_line_edit_4")
        self.lan_line_edit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lan_line_edit_2.setGeometry(QtCore.QRect(240, 120, 31, 21))
        self.lan_line_edit_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lan_line_edit_2.setReadOnly(False)
        self.lan_line_edit_2.setObjectName("lan_line_edit_2")
        self.lan_line_edit_1 = QtWidgets.QLineEdit(self.centralwidget)
        self.lan_line_edit_1.setGeometry(QtCore.QRect(200, 120, 31, 21))
        self.lan_line_edit_1.setAlignment(QtCore.Qt.AlignCenter)
        self.lan_line_edit_1.setReadOnly(False)
        self.lan_line_edit_1.setObjectName("lan_line_edit_1")
        self.lan_line_edit_3 = QtWidgets.QLineEdit(self.centralwidget)
        self.lan_line_edit_3.setGeometry(QtCore.QRect(280, 120, 31, 21))
        self.lan_line_edit_3.setAlignment(QtCore.Qt.AlignCenter)
        self.lan_line_edit_3.setReadOnly(False)
        self.lan_line_edit_3.setObjectName("lan_line_edit_3")
        self.dot4_label = QtWidgets.QLabel(self.centralwidget)
        self.dot4_label.setGeometry(QtCore.QRect(230, 120, 16, 17))
        self.dot4_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot4_label.setObjectName("dot4_label")
        self.dot6_label = QtWidgets.QLabel(self.centralwidget)
        self.dot6_label.setGeometry(QtCore.QRect(310, 120, 16, 17))
        self.dot6_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot6_label.setObjectName("dot6_label")
        self.dot5_label = QtWidgets.QLabel(self.centralwidget)
        self.dot5_label.setGeometry(QtCore.QRect(270, 120, 16, 17))
        self.dot5_label.setAlignment(QtCore.Qt.AlignCenter)
        self.dot5_label.setObjectName("dot5_label")
        self.lan_line_edit_4 = QtWidgets.QLineEdit(self.centralwidget)
        self.lan_line_edit_4.setGeometry(QtCore.QRect(320, 120, 31, 21))
        self.lan_line_edit_4.setAlignment(QtCore.Qt.AlignCenter)
        self.lan_line_edit_4.setReadOnly(False)
        self.lan_line_edit_4.setObjectName("lan_line_edit_4")
        self.port_label = QtWidgets.QLabel(self.centralwidget)
        self.port_label.setGeometry(QtCore.QRect(30, 150, 67, 31))
        self.port_label.setObjectName("port_label")
        self.port_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.port_line_edit.setGeometry(QtCore.QRect(70, 150, 51, 31))
        self.port_line_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.port_line_edit.setObjectName("port_line_edit")
        self.log_label = QtWidgets.QLabel(self.centralwidget)
        self.log_label.setGeometry(QtCore.QRect(20, 200, 141, 17))
        self.log_label.setObjectName("log_label")
        ReceiverWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ReceiverWindow)
        QtCore.QMetaObject.connectSlotsByName(ReceiverWindow)

    def retranslateUi(self, ReceiverWindow):
        _translate = QtCore.QCoreApplication.translate
        ReceiverWindow.setWindowTitle(_translate("ReceiverWindow", "MainWindow"))

        self.start_stop_button.setText(_translate("ReceiverWindow", "Start receiver"))
        self.start_stop_button.clicked.connect(self.start_receiver)

        self.probability_label.setText(_translate("ReceiverWindow", "Probabilitatea de pierdere a pachetelor (%):"))
        self.progres_bar_label.setText(_translate("ReceiverWindow", "Progres transfer:"))
        self.probability_line_edit.setText(_translate("ReceiverWindow", "0"))
        self.probability_line_edit.setValidator(QIntValidator(0, 100))

        self.log_label.setText(_translate("ReceiverWindow", "Log-ul transferului:"))
        self.dot1_label.setText(_translate("ReceiverWindow", "."))
        self.dot2_label.setText(_translate("ReceiverWindow", "."))
        self.dot3_label.setText(_translate("ReceiverWindow", "."))
        self.dot4_label.setText(_translate("ReceiverWindow", "."))
        self.dot5_label.setText(_translate("ReceiverWindow", "."))
        self.dot6_label.setText(_translate("ReceiverWindow", "."))

        self.loopback_radio_button.setText(_translate("ReceiverWindow", "Adresa IP de loopback:"))
        self.lan_radio_button.setText(_translate("ReceiverWindow", "Adresa IP din LAN:"))

        self.loopback_radio_button.toggled.connect(self.on_radio_button)
        self.lan_radio_button.toggled.connect(self.on_radio_button)

        self.loopback_line_edit_1.setText(_translate("ReceiverWindow", "127"))
        self.loopback_line_edit_2.setText(_translate("ReceiverWindow", "0"))
        self.loopback_line_edit_3.setText(_translate("ReceiverWindow", "0"))
        self.loopback_line_edit_4.setText(_translate("ReceiverWindow", "1"))

        self.lan_line_edit_1.setText(_translate("ReceiverWindow", "192"))
        self.lan_line_edit_2.setText(_translate("ReceiverWindow", "168"))
        self.lan_line_edit_3.setText(_translate("ReceiverWindow", "0"))       
        self.lan_line_edit_4.setText(_translate("ReceiverWindow", "0"))

        self.lan_line_edit_1.setValidator(QIntValidator(0, 255))
        self.lan_line_edit_2.setValidator(QIntValidator(0, 255))
        self.lan_line_edit_3.setValidator(QIntValidator(0, 255))
        self.lan_line_edit_4.setValidator(QIntValidator(0, 255))

        self.port_label.setText(_translate("ReceiverWindow", "Port:"))
        self.port_line_edit.setText(_translate("ReceiverWindow", "1234"))
        self.port_line_edit.setValidator(QIntValidator(1234, 65535))

    def on_radio_button(self):
        if self.loopback_radio_button.isChecked():
            self.ip_address = "127.0.0.1"
        elif self.lan_radio_button.isChecked():
            self.ip_address = self.lan_line_edit_1.text() + '.' + self.lan_line_edit_2.text() + '.' + self.lan_line_edit_3.text() + '.' + self.lan_line_edit_4.text()

    def write_in_log(self, message):
        self.log_plain_text.appendPlainText(message)

    def start_receiver(self):

        if self.start_stop_button.isChecked() == True:

            self.probability = int(self.probability_line_edit.text())

            try:
                self.port = int(self.port_line_edit.text())
                if self.port < 1234:
                    raise ValueError("Portul trebuie sa fie cuprins intre 1234 si 65535.")

            except ValueError as e:
                msg = QMessageBox()
                msg.setStyleSheet("QLabel{min-width: 250px;}");
                msg.setWindowTitle("Eroare!")
                msg.setInformativeText(str(e))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                return

            self.receiver.set_ip_address(self.ip_address)
            self.receiver.set_port(self.port)
            self.receiver.set_probability(self.probability)

            self.receiver.create_socket("AF_INET", "SOCK_DGRAM")

            self.thread = threading.Thread(target=self.receiver.start_receiver)
            self.thread.start()
            self.start_stop_button.setText("Stop Receiver")
        else:
            self.receiver.set_is_running(False)
            
            data_packet = SWPacket(self.receiver.DATA_PACKET_SIZE, self.receiver.DATA_SIZE, self.receiver.PACKET_HEADER_SIZE, packet_type=PacketType.DATA)
            data_packet.make_end_packet()
            data_packet.set_packet_number(0xFFFFFF)
            
            self.receiver.get_socket().sendto(data_packet.get_data(), (self.receiver.get_ip_address(), self.receiver.get_port()))
            self.start_stop_button.setText("Start Receiver")


if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    ReceiverWindow = QtWidgets.QMainWindow()
    ui = ReceiverGUI()
    ui.setupUi(ReceiverWindow)
    ReceiverWindow.show()
    sys.exit(app.exec_())

