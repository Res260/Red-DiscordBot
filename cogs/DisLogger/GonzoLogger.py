import logging as log

from cogs.DisLogger.Handlers.DiscordHandler import DiscordHandler
from cogs.DisLogger.Handlers.SMSHandler import SMSHandler
'''

class GonzoLogger:
	"""
	A class that manages the loggers.
	"""
	def __init__(self, bot):
		"""
		Creates a new instance of GonzoLogger with all the good handlers
		and loggers and formatters.
		"""
		self.MAIN_LOGGER = "main"
		self.DISCORD_LOGGER = self.MAIN_LOGGER + ".discordLogger"
		self.SMS_LOGGER = self.DISCORD_LOGGER+ ".smsLogger"
		self.MAIN_FORMAT = "[%(asctime)s] %(levelname)-8s->%(message)s"
		self.DISCORD_FORMAT = "```Markdown\n<%(asctime)-23s> <%(levelname)s>\n%(message)s"

		self.__mainLogger = log.getLogger(self.MAIN_LOGGER)
		self.__mainLogger.setLevel(log.DEBUG)
		self.__mainLogger.addHandler(self.get_main_handler())

		self.__discordLogger = log.getLogger(self.DISCORD_LOGGER)
		self.__discordLogger.setLevel(log.DEBUG)
		self.__discordLogger.addHandler(self.get_discord_handler(bot))

		self.__smsLogger = log.getLogger(self.SMS_LOGGER)
		self.__smsLogger.setLevel(log.DEBUG)
		self.__smsLogger.addHandler(self.get_sms_handler())

	def get_main_logger(self):
		"""
		:return: The main Logger
		"""
		return self.__mainLogger

	def get_main_handler(self):
		"""
		:return: The main handler (File logging)
		"""
		handler = log.FileHandler("data/DisLogger/main.log", encoding="UTF-8")
		# handler = log.StreamHandler()
		handler.setLevel(log.DEBUG)
		handler.setFormatter(self.get_main_formatter())

		return handler

	def get_main_formatter(self):
		"""
		:return: The main formatter (Basic one line string)
		"""
		return log.Formatter(self.MAIN_FORMAT)

	def get_discord_logger(self):
		return self.__discordLogger

	def get_discord_handler(self, bot):
		handler = DiscordHandler(bot)
		handler.setFormatter(self.get_discord_formatter())
		return handler

	def get_discord_formatter(self):
		return log.Formatter(self.DISCORD_FORMAT + "```")

	def get_sms_logger(self):
		return self.__smsLogger

	def get_sms_handler(self):
		handler = SMSHandler("18193145680")
		handler.setLevel(log.ERROR)
		handler.setFormatter(self.get_main_formatter())
		return handler

'''