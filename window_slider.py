class Window_slider:
    def __init__(self,window_size):
        self.__windows_size = window_size
        self.__current_packages_sent = 0

        self.__packages_received = []

    def send_packages(self):
        self.__current_packages_sent += 1

    def receive_packages(self):
        self.__current_packages_sent -= 1