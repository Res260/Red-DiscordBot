import abc
from threading import Thread
import calendar
import time
from scapy.all import ARP, arping


class Monitor(abc.ABC):
	"""
	Abstract class that defines a monitor for the application.
	A monitor runs in a separated thread and calls its logger.
	"""


	def __init__(self, logger):
		"""
		Creates a new instance of Monitor with a logger. The implementation is
		defined by the class' children.
		:param logger: The logger to use while monitoring.
		"""
		self._logger = logger
		self._is_monitoring = False
		self._continue_monitor_token = False
		self.monitoring_thread = Thread(target=self.monitoring_loop)


	def start_monitoring(self):
		"""
		Starts the monitoring thread.
		"""
		self._logger.info("Started monitoring.")
		self._continue_monitor_token = True
		self.monitoring_thread.start()
		self._is_monitoring = True


	def stop_monitoring(self):
		"""
		Sets the monitoring token to false, joins the monitoring thread and
		gently logs that the monitoring process has ended.
		"""
		self._continue_monitor_token = False
		self.monitoring_thread.join()
		self._is_monitoring = False
		self._logger.info("Stopped monitoring.")

	@abc.abstractmethod
	def monitoring_loop(self):
		"""
		The loop that is runned in a separate Thread. Implementation is left to the
		child class.
		"""
		pass

	def is_monitoring(self):
		"""
		:return: True if the monitoring process is active.
		"""
		return self._is_monitoring


class ARPMonitor(Monitor):
	"""
	Monitor class that uses the arp protocol to ping an ip, and logs
	whether the ip is there or not.
	"""

	def __init__(self, logger=None, ip=None):
		"""
		Creates a new instance of ARPMonitor.
		:param logger: The logger of the monitor.
		:param ip: The ip to arping.
		"""
		super(ARPMonitor, self).__init__(logger)
		self.logger = logger
		self.ip = ip
		self.__last_sign = 0

	def monitoring_loop(self):
		"""
		The threaded loop to monitor ARP Connections.
		"""

		self.messageSent = True
		last_log_time = 0
		LOG_SECONDS_INTERVAL = 3
		while self._continue_monitor_token:
			current_time = calendar.timegm(time.gmtime())
			if not self.__is_there():
				if current_time - last_log_time > LOG_SECONDS_INTERVAL:
					msg = self.ip + " gave no sign of life since " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.__last_sign)))
					if not self.messageSent:
						self.logger.error(msg)
					self.messageSent = True
					self.logger.warning(msg)
					last_log_time = current_time
			else:
				self.messageSent = False
				if current_time - last_log_time > LOG_SECONDS_INTERVAL:
					self.logger.info(self.ip + " is CONNECTED. Last sign of life: " + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.__last_sign))))
					last_log_time = current_time
			time.sleep(2)

	def __is_there(self):
		"""
		SIDE EFFECT ON self.__last_sign
		:return: True if the ip responded at least once in 
		         the last self.__last_sign seconds. 
		"""
		current_time = calendar.timegm(time.gmtime())
		is_there = True
		if not self.__is_connected():
			if current_time - self.__last_sign > 300:
				is_there = False
		else:
			self.__last_sign = current_time
		return is_there

	def __is_connected(self):
		"""
		Sends an arping request to self.ip.
		:return: True if a response from self.ip was received.
		"""
		is_connected = False
		answers, uns = arping(self.ip + "/32", timeout=1, verbose=False)
		for answer in answers:
			if answer[1].getlayer(ARP).psrc == self.ip:
				is_connected = True
		return is_connected
