from pathlib import Path

"""
	Clasa folosita pentru a citi un fisier
"""
class FileReader:
	def __init__(self, filename, bytes_per_read):
		self.__filename = filename
		self.__file = None
		self.__size_in_bytes = 0
		self.__no_of_bytes_per_read = bytes_per_read

	def open(self):
		self.__file=open(self.__filename, 'rb')
		self.__size_in_bytes = Path(self.__filename).stat().st_size

	def close(self):
		self.__file.close()

	def read(self):
		return self.__file.read(self.__no_of_bytes_per_read)

	def get_bytes_per_read(self):
		return self.__no_of_bytes_per_read

	def get_file_size_in_bytes(self):
		return self.__size_in_bytes