"""
Author: Kennan (Kenneract)

Purpose: An example of Simple-Vosk performing speech recognition as a background task.

Version: Python 3.8.7 (Windows)

Date: Jan.19.2022
"""

import simpleVosk as sv
import time

def printout(text:str, speaker:str, isFull:bool):
	# Callback; run on each text block.
	print(f"Heard: {text}")

speech = sv.Speech(callback=printout, model="model")
speech.start(blocking=False)
# Execution continues after this line!
runtime=0
while True:
	print(f"Script running for {runtime} seconds.")
	time.sleep(2) #Blocking function; Vosk continues to run in background
	runtime+=2