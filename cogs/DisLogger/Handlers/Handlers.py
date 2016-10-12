import abc

import twilio.rest
import logging as log


class Handler(abc.ABC, log.StreamHandler):
	def __init__(self, log_level=None):
		if not log_level:
			raise ValueError("You need to specify a log_level for every Handler.")
		super().__init__()
		super(log.StreamHandler, self).__init__(log_level)
		self.setLevel(log_level)


class SettingsDependantHandler(Handler):
	"""
	A class that represents a handler that needs to access values in the config.json file.
	"""

	def __init__(self, settings_manager=None, log_level=None):
		if not settings_manager:
			raise ValueError("A SettingsDependantHandler needs to have access to the SettingsManager. "
							 "Make sure to include it while creating the SettingsDependantHandler you wish to create.")
		super().__init__(log_level)
		self.__settings_manager = settings_manager


class DiscordHandler(Handler):

	def __init__(self, log_level=None, bot=None, channel_id=None):
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
		formatted_message = self.format(record)
		self.acquire()
		self.__bot.loop.create_task(
			self.__bot.send_message(
				self.__channel, formatted_message))
		self.release()


class SMSHandler(SettingsDependantHandler):

	def __init__(self, log_level=None, settings_manager=None, phone_number_destination=None):
		if not phone_number_destination:
			raise ValueError("SMSHandler needs to have phone_number_destination.")
		super().__init__(log_level, settings_manager)
		twilio_settings = self.__settings_manager.get_value("twilio")
		self.__client = twilio.rest.TwilioRestClient(twilio_settings["sid"], twilio_settings["secret"])
		self.__phone_number_destination = phone_number_destination

	def emit(self, record):
		"""
		Logs the message using the Twilio SMS service. A SMS will be sent to self.__phone_number_destination.
		:param record: The log record to handle.
		"""
		formatted_message = self.format(record)
		# sending the message vvvvvvv
		message = self.__client.messages.create(to="+" + self.__phone_number_destination,
										 from_="+18737001763",
										 body=formatted_message)