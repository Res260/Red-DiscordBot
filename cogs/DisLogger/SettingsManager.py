import logging as log
import os

import cogs.utils.dataIO as dataIO
import shutil
import cogs.DisLogger.Monitors.Monitors as monitors
import cogs.DisLogger.Handlers.Handlers as handlers


class SettingsManager:
	"""
	Class that manages the settings file for the application.
	"""

	DEFAULT_CONFIG_PATH = "./cogs/DisLogger/config_default.json"

	def __init__(self, bot, config_file_path="./data/DisLogger/config.json"):
		"""
		Creates a new instance of SettingsManager.
		:param bot: The Discord bot instance for the application. 
		:param config_file_path: The path of the config file of the application.
		"""
		self.__config_file_path = config_file_path
		self.__dataIO = dataIO.DataIO()
		self.__data = None
		self.__bot = bot

	def initiate(self):
		"""
		Creates a config file is none exists, and validates if the integrity of
		the config file is okay, as well as the rights to access. Loads the JSon
		in the class.
		"""
		if not os.path.isfile(self.__config_file_path):
			self.__copy_default_config_file()
		if not self.__dataIO.is_valid_json(self.__config_file_path):
			try:
				os.rename(self.__config_file_path, self.__config_file_path + "_corrupted")
			except:
				raise PermissionError("ERROR: Make sure to run the program as an"
									  " administrator. File access right is "
									  "limited at the moment.")
			print("Config file is corrupted. Make sure the file is either "
				  "accessible or that it's content is valid JSON. The file as "
				  "been renamed to {} and a new one has been"
				  "created.".format(self.__config_file_path + "_corrupted"))
			exit(1)
		else:
			self.__data = self.__dataIO.load_json(self.__config_file_path)

	def __copy_default_config_file(self):
		"""
		Copies the default config file to use as the config file for the application.
		"""
		if not os.path.exists(os.path.dirname(self.__config_file_path)):
			try:
				os.makedirs(os.path.dirname(self.__config_file_path))
			except OSError:
				raise PermissionError("Cannot create directory for {}."
									      .format(self.__config_file_path))

		shutil.copy(self.DEFAULT_CONFIG_PATH, self.__config_file_path)

	def get_value(self, key):
		"""
		Returns the value of the key in the config file.
		If the value contains an "#info#" key, it is ignored.
		:param key: The key to query.
		:return: The value of the key.
		"""
		uncleaned_data = self.__data[key]
		return_value = {}
		for key, value in uncleaned_data.items():
			if key[:4] != "#inf" and key[:4] != "####" :
				return_value[key] = value
		return return_value

	def set_value(self, key, value):
		"""
		Sets the value of key to value in the config file.
		:param key: Parameter to set.
		:param value: Value of the parameter
		"""
		dataIO.set_value(self.__config_file_path, key, value)

	def get_monitor(self, monitor):
		"""
		Returns an instance of monitor['type'], instantiated with the arguments
		set in monitor['config'].
		:param monitor: A JSon object containing at least 'type', 'logger'
		and 'config'.
		:return: An instance of a monitor, as requested by monitor['type'].
		"""
		if not isinstance(monitor, dict):
			raise ValueError("the argument is not a dictionary.")
		return_value = None
		try:
			monitor_class = eval("monitors." + monitor["type"])
			monitor["config"]["logger"] = self.get_logger(monitor["logger"])
			return_value = monitor_class(**monitor["config"])
		except:
			print("ERROR: The config file seems to be corrupted. Delete the file in data/DisLogger/config.json, launch "
				  "the program again, then try to modify the new config file.")
			exit(1)
		return return_value

	def get_logger(self, name):
		"""
		Returns an instance of Logger, as described in ConfigFile['loggers'].
		Sets the corresponding handler and the corresponding log level.
		:param name: The name of the instance.
		:return: A fully fonctionnal and configurated logger.
		"""
		logger = None
		if not isinstance(name, str):
			raise ValueError("the argument is not a string.")
		logger_dict = self.get_value("loggers")[name]
		logger = log.getLogger(name)
		logger.setLevel(logger_dict["log_level"])
		for handler_name, handler_instance in logger_dict["handlers"].items():
			logger.addHandler(self.get_handler(handler_instance))
		return logger

	def get_handler(self, name):
		"""
		Returns an instance of handler 'name' specified in the config file.
		:param name: The name of the instance of the handler.
		:return: The instance of the specific handler.
		"""
		if not isinstance(name, str):
			raise ValueError("the argument is not a string.")
		handler_dict = self.get_value("handlers")[name]
		handler_class = eval("handlers." + handler_dict["type"])
		handler = handler_class(bot=self.__bot, **handler_dict["config"])
		handler.setFormatter(self.get_formatter(handler_dict["formatter"]))
		return handler

	def get_formatter(self, name):
		"""
		Returns a Formatter instance, as defined in configFile['formatters']
		:param name: The name of the formatter.
		:return: A Formatter instance that can be used by Handler.setFormatter()
		"""
		return log.Formatter(self.get_value("formatters")[name])

