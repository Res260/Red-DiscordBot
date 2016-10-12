import logging as log

from cogs.utils.dataIO import *
from cogs.utils.dataIO import DataIO
import cogs.DisLogger.Monitors.Monitors as monitors
import cogs.DisLogger.Handlers.Handlers as handlers


class SettingsManager:

	def __init__(self, file_name, bot):
		self.__file_name = file_name
		self.__dataIO = DataIO()
		self.__data = None
		self.__bot = bot

	def initiate(self):
		"""
		Creates a config file is none exists, and validates if the integrity of
		the config file is okay, as well as the rights to access. Loads the JSon
		in the class.
		"""
		if not os.path.isfile(self.__file_name):
			self.__create_config_file()
		if not self.__dataIO.is_valid_json(self.__file_name):
			try:
				os.rename(self.__file_name, self.__file_name + "_corrupted")
			except:
				raise PermissionError("ERROR: Make sure to run the program as an"
									  " administrator. File access right is "
									  "limited at the moment.")
			print("Config file is corrupted. Make sure the file is either "
				  "accessible or that it's content is valid JSON. The file as "
				  "been renamed to {} and a new one has been"
				  "created.".format(self.__file_name + "_corrupted"))
			exit(1)
		else:
			self.__data = self.__dataIO.load_json(self.__file_name)

	def __create_config_file(self):
		config = {
            "server": {
                "id": "229390802344738817",
                "main_channel_name": "general"
            },
            "monitors": {
                "ARPMonitor1": {
                    "type": 	"ARPMonitor",
					"logger": 	"main",
                    "config": {
                        "ip": "192.168.0.140"
                    }
                },

				"ARPMonitorGui": {
					"type": 	"ARPMonitor",
					"logger": 	"main.test",
					"config": {
						"ip": "10.60.9.128"
					}
				}
            },

			"loggers": {
				"main": {
					"log_level": 20,
					"handlers": {
						"handler1": "DiscordHandlerGeneral"
					}
				},

				"main.test": {
					"log_level": 20,
					"handlers": {
						"handler1": "DiscordHandlerOtherChannel"
					}
				},

				"#infO#": "### HERE YOU SPECIFY THE LOGGER INSTANCES YOU WISH TO USE. A LOGGER CAN   ###",
				"#inf.#": "### INHERIT ANOTHER LOGGER. IT WORKS LIKE THIS: grandparent.parent.child  ###",
				"#infc#": "###  WHAT IT DOES IS IT THAT IF YOU LOG SOMETHING WITH THE CHILD LOGGER,  ###",
				"#infq#": "### IT WILL ALSO LOG USING ITS PARENTS. YOU ALSO SPECIFY THE INSTANCES OF ###",
				"#inf0#": "### HANDLERS YOU WISH TO USE FOR YOUR LOGGER. THE LOG LEVELS CAN BE FOUND ###",
				"#inf*#": "###  HERE: https://docs.python.org/3/library/logging.html#logging-levels  ###",
				"#info#": "###            IF YOU DONT KNOW WHAT IT IS, KEEP IT AT 20.                ###",
			},

			"handlers": {
				"DiscordHandlerGeneral": {
					"type": 	"DiscordHandler",
					"formatter":"Discord",
					"config": {
						"log_level": 	20,
						"channel_id": 	"229391297754955797"
					}
				},

				"DiscordHandlerOtherChannel": {
					"type": "DiscordHandler",
					"formatter": "Discord",
					"config": {
						"log_level": 20,
						"channel_id": "233016092816048128"
					}
				},

				"#infu#": "###            THE ARGUMENTS NEEDED TO CREATE A HANDLER OBJECT.           ###",
				"#infO#": "### THE FORMATTER IS A NAME OF A FORMATTER INSTANCE. CONFIG CONSISTS OF   ###",
				"#inf0#": "###   THE CLASS NAME OF THE HANDLER(FOUND IN cogs/DisLogger/Handlers.py)  ###",
				"#info#": "### HERE YOU SPECIFY THE HANDLERS INSTANCES YOU WISH TO USE. THE TYPE IS  ###",

			},

			"formatters": {
				"Main": 	"[%(asctime)s] %(levelname)-8s->%(message)s",
				"Discord": 	"```Markdown\n<%(asctime)-23s> <%(levelname)s>\n%(message)s\n```",
				"SMS": 		"[%(asctime)s] %(levelname)-8s:\n%(message)s",

				"#info#": "###    https://docs.python.org/3/library/logging.html#formatter-objects   ###",
				"#infO#": "###                 FOR MORE INFORMATION, HEAD THERE:                     ###",
				"#inf0#": "### THIS IS WHERE YOU SPECIFY THE FORMATTING INSTANCES FOR THE HANDLERS.  ###",
			},

			"twilio": {
				"sid": 		"AC0d32c011d52f2f90123e7cda99b94757",
				"secret": 	"c54b17c56fd10eb05ddd557078a5da44",
				"#info#": "### YOU CAN CREATE A FREE ACCOUNT AT: https://www.twilio.com/try-twilio.  ###",
				"#infO#": "###     THIS IS WHERE YOU SPECIFY YOUR TWILIO ACCOUNT API KEY VALUES.     ###",
			},

			"#info#": "###            KEYS AND MAKE YOUR APPLICATION BEHAVE AS YOU WISH.             ###",
			"#infO#": "### THAT YOU CAN MODIFY. TO KNOW WHAT TO CHANGE, JUST LOOK AT OTHER '#info#'  ###",
			"#inf0#": "###THIS IS THE CONFIG FILE FOR THE DISLOGGER APPLICATION. IT IS A SAMPLE FILE ###",
        }
		self.__dataIO.save_json(self.__file_name, config)

	def get_value(self, key):
		"""
		Returns the value of the key in the config file.
		If the value contains an "#info#" key, it is ignored.
		:param key: The key to query.
		:return: The value of the key.
		"""
		return_value = self.__data[key]
		for key in return_value:
			if key[:4] == "#inf":
				del(return_value[key])
		return return_value

	def set_value(self, key, value):
		set_value(self.__file_name, key, value)

	def get_monitor(self, monitor):
		"""
		Returns an instance of monitor['type'], instantiated with the arguments
		set in monitor['config'].
		:param monitor: A JSon object containing at least 'type'
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

