import abc

import twilio.rest
import logging as log


class Handler(abc.ABC, log.StreamHandler):
	"""
	Abstract class that defines a log handler, which is 
	responsible to actually log the information to the right place.
	It has a log level (see: https://docs.python.org/3.5/howto/logging.html#when-to-use-logging).
	"""

	def __init__(self, log_level=None):
		"""
		Creates a new instance of handler with a log level.
		:param log_level: The minimal log level where the handler will listen to log calls.
		"""
		if not log_level:
			raise ValueError("You need to specify a log_level for every Handler.")
		super().__init__()
		super(log.StreamHandler, self).__init__(log_level)
		self.setLevel(log_level)


class SettingsDependantHandler(Handler):
	"""
	A handler class that represents a handler that needs to access
	values in the config.json file.
	"""

	def __init__(self, settings_manager=None, log_level=None):
		"""
		Creates a new instance of SettingsDependantHandler.
		:param settings_manager: The app's settings manager.
		:param log_level: The minimal log level where the handler will listen to log calls.
		"""
		if not settings_manager:
			raise ValueError("A SettingsDependantHandler needs to have access to the SettingsManager. "
							 "Make sure to include it while creating the "
							 "SettingsDependantHandler you wish to create.")
		super().__init__(log_level)
		self.__settings_manager = settings_manager


class DiscordHandler(Handler):
	"""
	Handler class that logs to a discord channel.
	"""

	def __init__(self, log_level=None, bot=None, channel_id=None):
		"""
		Creates a new insance of DiscordHandler.
		:param log_level: The minimal log level where the handler will listen to log calls.
		:param bot: The bot instance to log to Discord.
		:param channel_id: The channel id to log to.
		"""
		if not bot:
			raise ValueError("DiscordHandler needs to have a bot. Make sure to include "
							 "it while creating a DiscordHandler.")
		if not channel_id:
			raise ValueError("DiscordHandler needs to have a channel_id. Make sure to include "
							 "it while creating a DiscordHandler.")
		super().__init__(log_level)
		self.__bot = bot
		self.__channel = self.__bot.get_channel(channel_id)

	def emit(self, record):
		"""
		Sends the message to Discord.
		:param record: The object that contains the message and other metadata.
		"""
		formatted_message = self.format(record)
		self.acquire()
		self.__bot.loop.create_task(
			self.__bot.send_message(
				self.__channel, formatted_message))
		self.release()


class SMSHandler(SettingsDependantHandler):
	"""
	Handler that sends a SMS to a phone number using Twilio.
	"""

	def __init__(self, log_level=None, settings_manager=None, phone_number_destination=None):
		"""
		Creates a new instance of SMSHandler.
		:param log_level: The minimal log level where the handler will listen to log calls.
		:param settings_manager: The app's settings manager.
		:param phone_number_destination: The phone number to send the sms to.
		"""
		if not phone_number_destination:
			raise ValueError("SMSHandler needs to have phone_number_destination.")
		super().__init__(log_level, settings_manager)
		twilio_settings = self.__settings_manager.get_value("twilio")
		self.__client = twilio.rest.TwilioRestClient(twilio_settings["sid"], twilio_settings["secret"])
		self.__phone_number_destination = phone_number_destination

	def emit(self, record):
		"""
		Logs the message using the Twilio SMS service. A SMS will be sent
		to self.__phone_number_destination.
		:param record: The log record to handle.
		"""
		PHONE_PREFIX = "+"
		formatted_message = self.format(record)
		self.__client.messages.create(to=PHONE_PREFIX + self.__phone_number_destination,
										 from_="+18737001763",
										 body=formatted_message)
