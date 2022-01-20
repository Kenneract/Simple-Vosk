"""
Author: Kennan (Kenneract / Kunge)

Purpose: Simple-Vosk; a series of methods and a class that make using Vosk dead-simple.

Version: Python 3.8.7 (Windows)

Created: Dec.14.2021 (Initial release: Jan.19.2022)

Updated: Jan.19.2022
"""


import os #Checking if model paths exist
import queue #Vosk
import sounddevice as sd #Vosk
import vosk #Vosk
import sys #Print to stderr
import json #Processing Vosk outputs
import numpy as np #Voice-Signature distance calculation
import threading #Non-blocking execution


def simpleCallback(text:str, speaker:str, isFull:bool):
	"""
	An example callback that can be fed to a Speech() class.
	"""
	state = "Full" if (isFull) else "Partial"
	if (speaker is None):
		print(f"\n[{state}] {text}")
	else:
		print(f"\n[{state}] {speaker}: {text}")

def listDevices(self):
	"""
	Prints all the sound devices to the screen - only for initial setup.
	"""
	print(sd.query_devices())

class Speech():
	"""
	A simple wrapper for real-time (from microphone) speech-to-text and
	speaker-recognition using Vosk.
	"""

	def __init__(self, callback=simpleCallback, partial:bool=False, model:str="model",
					speakModel:str=None, signatures:dict={}, maxSpeakThresh:float=0.54,
					filterText:bool=True, printUnknownSigs:bool=True, deviceID:int=None,
					verbose:bool=False):
		"""
		Generates a Speech object. Run Speech.start() to start voice recognition.

		PARAMS:
		callback
			Function to call when voice data is processed. Must accept arguments
			(text:str,speakerName:str,isFull:bool). See the "simpleCallback" method.
		partial:bool
			If True, will run the callback in real-time as text is processed as
			the speaker is talking. This allows for faster response times, but
			accuracy is lower and speaker-recognition is not available.
		model:str
			Path to the Vosk model.
		speakModel:str
			Path to the speaker-recognition Vosk model. (Optional; passing None
			disables speaker recognition)
		signatures:dict
			Dict of {"Speaker":[X-Vector]} speaker-signature pairs.
		maxSpeakThresh:float
			The maximum cosine distance to accept a voice signature match.
			Smaller values mean tighter tolerances.
		filterText:bool
			If should filter common false-triggers from running the callback (ex.
			Vosk sometimes pulls a "huh" from silence)
		printUnknownSigs:bool
			If unreogniced speaker signatures (X-Vectors) should be printed to
			console (good for setting up new signatures).
		deviceID:int
			The device number from listDevices(). None appears to use the
			system-default device.
		verbose:bool
			If should print debug data (such as voice signature x-vector distances)
		"""
		#vosk-specific
		self.__q = queue.Queue() #Queue for audio block data; comm. between threads
		self.__model = model
		self.__spkModel = speakModel
		self.__deviceID = deviceID
		#text-to-speech configuration
		self.__callback=callback
		self.__partial=partial
		self.__filterText=filterText
		self.__textFilters = ["huh","by","but"] #filterText phrases to ignore
		#speaker-recognition configuration
		self.__verbose = verbose
		self.__speakSigs = signatures
		self.__maxSpeakDist = maxSpeakThresh
		self.__printUnknownSigs = printUnknownSigs
		#internal
		self.__running=False
		self.__thread=None #The background thread that Vosk is running in.

	def start(self, blocking:bool=False):
		"""
		Begins the vosk speech recognition in a background thread and will start
		running the callbacks. Can optionally run in foreground, causing this
		method to block further execution.
		"""
		self.__running=True
		if (blocking):
			## Run Vosk in foreground, blocking execution.
			self.__runVosk()
		else:
			## Run Vosk in background thread as to not block.
			self.__thread = threading.Thread(target=self.__runVosk)
			self.__thread.daemon = True
			self.__thread.start()

	def stop(self):
		"""
		Terminates the background thread, if running, haulting voice recognition.
		"""
		self.__running=False
	
	def isRunning(self):
		"""
		Returns if speech recognition is currently running.
		"""
		return self.__running

	def addFilterWords(self, words:list):
		"""
		Adds the words in the provided list to the text filter.
		"""
		self.__textFilters += words

	def __cosineDist(self, x, y):
		"""
		Taken from vosk python examples. Calculates the cosine distance between two
		lists of values. Used for voice signature comparisons.
		"""
		nx = np.array(x)
		ny = np.array(y)
		return 1 - np.dot(nx, ny) / np.linalg.norm(nx) / np.linalg.norm(ny)

	def __speakerCheck(self, load):
		"""
		Given the output payload from vosk in JSON form, checks if the voice signature
		matches any known ones.
		
		Returns the name behind the best-matching voice signature. Returns None if
		insufficient data or no matching signature is found.
		"""
		## Ensure speaker data is present
		if ("spk" not in load):
			return None
		## Check voice signatures for best-fit
		#num frames = load['spk_frames']
		minDist=self.__maxSpeakDist*2
		bestFit=None
		for person in self.__speakSigs:
			sig = self.__speakSigs[person]
			dist = self.__cosineDist(sig, load['spk'])
			if (self.__verbose): print(f"Distance: {person}: {dist:.4f}")
			if (dist < minDist):
				minDist=dist
				bestFit=person
		## Ensure above speaker thresh
		if (minDist > self.__maxSpeakDist):
			if (self.__printUnknownSigs):
				print ("Unknown X-vector:", load['spk'])
			return None
		## Return best-fit person
		return bestFit

	def __checkCallback(self, data):
		"""
		Given the raw output result from vosk, checks if sufficient text data was
		provided, runs speaker identification (if enabled), and runs the callback.
		
		Takes into consideration: partial vs. full text setting, filter text list,
		and speaker recognition setting.
		"""
		## Convert raw result into JSON structure
		load=json.loads(data)
		if ("text" in load):
			s = load["text"]
			if (len(s)>0):
				## Check text filter
				if (self.__filterText and s in self.__textFilters):
					return None
				## Check speaker data if enabled
				speaker=None
				if (self.__spkModel is not None):
					speaker = self.__speakerCheck(load)
				self.__callback(s,speaker,True)
		elif (self.__partial and "partial" in load):
			s = load["partial"]
			if (len(s)>0): 
				## Check text filter
				if (self.__filterText and s in self.__textFilters):
					return None
				## Run callback
				self.__callback(s,None,False)

	def __voskCallback(self, indata, frames, time, status):
		"""
		This is called (from a separate thread) for each audio block.
		"""
		if (status and self.__verbose):
			print(status, file=sys.stderr)
		self.__q.put(bytes(indata))

	def __runVosk(self):
		"""
		Start the raw input stream from the microphone, initializes Vosk's
		KaldiRecognizer, and begins parsing audio to speech data. The core
		of the voice recognition.
		"""
		sampleRate=None #None uses default for device
		## Ensure models exist
		if (not os.path.exists(self.__model)):
			print ("Download a model from https://alphacephei.com/vosk/models")
		if (self.__spkModel is not None and not os.path.exists(self.__spkModel)):
			print ("Download the speaker model from https://alphacephei.com/vosk/models")
		## Use default sample rate if none defined
		if (sampleRate is None):
			deviceInfo = sd.query_devices(self.__deviceID, 'input')
			# soundfile expects an int, sounddevice provides a float:
			sampleRate = int(deviceInfo['default_samplerate'])
		## Load model(s)
		model = vosk.Model(self.__model)
		if (self.__spkModel is not None):
			spkModel = vosk.SpkModel(self.__spkModel)
		## Processing loop
		with sd.RawInputStream(samplerate=sampleRate, blocksize=8000,
								device=self.__deviceID, dtype='int16',
								channels=1, callback=self.__voskCallback):
			rec = vosk.KaldiRecognizer(model, sampleRate)
			if (self.__spkModel is not None): rec.SetSpkModel(spkModel)
			while self.__running:
				data = self.__q.get()
				if rec.AcceptWaveform(data):
					self.__checkCallback(rec.Result()) #Callback w/ full data
				else:
					self.__checkCallback(rec.PartialResult()) #Callback w/ partial data