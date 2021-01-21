
#	Clasa folosita pentru gestionarea comportametului de scriere intr-un fisier
#	Clasa contine o referinta la un fisier

#	writeInFile(self, data) - Scrierea unui array de octeti in fisier
#	setFileName(self, name) - Seteaza numele fisierului si elimina
#	openFile(self) - Imi deschide fisierul
#	closeFile(self) - Imi inchide fisierul
#	isOpen(self) - Imi returneaza starea fisierului (deschis/inchis)
class FileWriter:

	def __init__(self, filename):

		self.__is_open = False
		self.__filename = filename
		self.__output_file = None

	def write_in_file(self, data):
		 self.__output_file.write(data)

	def set_file_name(self, name):

		self.__filename = name

	def open_file(self):
		self.__is_open = True
		self.__output_file = open(self.__filename, "wb")

	def close_file(self):
		self.__is_open = False
		self.__output_file.close()

	def is_open(self):
		return self.__is_open

