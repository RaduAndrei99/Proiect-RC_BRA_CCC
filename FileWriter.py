
#	Clasa folosita pentru gestionarea comportametului de scriere intr-un fisier
#	Clasa contine o referinta la un fisier

#	writeInFile(self, data) - Scrierea unui array de octeti in fisier
#	setFileName(self, name) - Seteaza numele fisierului si elimina
#	openFile(self) - Imi deschide fisierul
#	closeFile(self) - Imi inchide fisierul
#	isOpen(self) - Imi returneaza starea fisierului (deschis/inchis)

class FileWriter:

	def __init__(self, filename):

		self.__isOpen = False
		self.__filename = filename
		self.__output_file = None

	def writeInFile(self, data):
		 self.__filename.write(data)

	def setFileName(self, name):
		name.replace('\0', '')
		name += '\0'

		self.__filename = name

	def openFile(self):
		self.__isOpen = True
		self.__output_file = open(self.__filename, "wb")

	def closeFile(self):
		self.__output_file.close()

	def isOpen(self):
		return self.__isOpen

