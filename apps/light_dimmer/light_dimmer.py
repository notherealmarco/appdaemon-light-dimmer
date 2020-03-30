import appdaemon.plugins.hass.hassapi as hass

class NoTheDimmer(hass.Hass):

	def initialize(self):
		self.log("notherealmarco's dimmer initialized!")
		self.default_speed = 0.1
		self.default_step = 15
		if "default_speed" in self.args:
			self.default_speed = self.args["default_speed"]
		if "default_step" in self.args:
			self.default_step = self.args["default_step"]
		self.listen_event(self.callback, "REAL_DIMMER")
		self.running = False
		self.current_direction = True

	def callback(self, event_name, data, kwargs):
		self.current_entities = data["entities"]
		self.current_speed = self.default_speed
		self.current_step = self.default_step
		if "speed" in data:
			self.current_speed = data["speed"]
		if "step" in data:
			self.current_step = data["step"]
		if data["direction"] == "down": self.current_direction = False
		if data["direction"] == "up": self.current_direction = True
		if data["direction"] == False: self.current_direction = False
		if data["direction"] == True: self.current_direction = True
		if data["direction"] == "auto":
			if self.current_direction: self.current_direction = False
			else: self.current_direction = True
			for d in self.current_entities:
				b = self.get_state(entity_id = d, attribute = "brightness")
				if b > 240: self.current_direction = False
				if b < 30: self.current_direction = True
		if data["direction"] == "stop": self.running = False
		else:
			self.running = True
			self.start_brightness(None)

	def start_brightness(self, b):
		for d in self.current_entities:
			b = self.get_state(entity_id = d, attribute = "brightness")
			if self.current_direction:
				n = b + self.current_step
			else:
				n = b - self.current_step
			if n < 1:
				self.turn_on(d, brightness = 1)
				return
			if n > 255:
				self.turn_on(d, brightness = 255)
				return
			self.turn_on(d, brightness = n)
		if self.running: self.run_in(self.start_brightness, self.current_speed)