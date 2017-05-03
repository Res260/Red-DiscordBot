#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import calendar
import logging as log
from discord.ext import commands

from cogs.DisLogger.SettingsManager import SettingsManager


class DisLogger:

	def __init__(self, bot):
		"""
		Creates a new instance of DisLogger with the bot object.
		:param bot:
		"""

		self.__SettingsManager = SettingsManager(bot)
		self.__SettingsManager.initiate()

		self.bot = bot
		self.is_currently_logging = False
		self.monitors = {}
		self.app_logger = log.getLogger("app")
		self.app_logger.addHandler(log.StreamHandler())
		self.app_logger.info("App Logger initialized.")

	@commands.command(pass_context=True)
	async def start_logging(self):
		"""
		Starts the logging process.
		"""
		self.app_logger.info("start_logging called.")
		self.is_currently_logging = True
		for monitor_name, monitor_content in \
				self.__SettingsManager.get_value("monitors").items():
			self.app_logger.info("Setting up monitor: {}".format(monitor_name))
			self.monitors[monitor_name] = self.__SettingsManager.get_monitor(monitor_content)

		for monitor_name, monitor in self.monitors.items():
			self.app_logger.info("Starting monitor: {}".format(monitor_name))
			monitor.start_monitoring()
			await self.bot.say(":up: {} started monitoring.".format(monitor_name))

	@commands.command(pass_context=True)
	async def stop_logging(self, context):
		await self.bot.say("Stopping the monitoring system...")
		for name, monitor in self.monitors.items():
			await self.bot.say(
				":arrows_counterclockwise: Stopping {} .".format(name))
			monitor.stop_monitoring()
			await self.bot.say(":arrow_down: {} Stopped monitoring.".format(name))
		await self.bot.say(":white_check_mark: Stop monitoring systems done.")
		self.is_currently_logging = False


# OUT OF CLASS
def setup(bot):
	"""
	Setups the cog (mandatory for RedBot).
	"""
	bot.add_cog(DisLogger(bot))