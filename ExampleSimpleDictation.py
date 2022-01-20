"""
Author: Kennan (Kenneract)

Purpose: An example of Simple-Vosk performing basic speech recognition
		(text-to-speech).

Version: Python 3.8.7 (Windows)

Date: Jan.19.2022
"""

"""
USAGE:

Run the script and begin speaking. As you speak, a partial output will be
displayed on screen. Once you finish speaking, the finalized string will
be printed. Note partial text output is less accurate than final output.

Set partial=False to disable the real-time partial text output.
"""

import simpleVosk as sv

def printout(text:str, speaker:str, isFull:bool):
	# Callback; run on each text block.
	if (isFull):
		print(f"-> Final: {text}")
	else:
		print(f"\tOngoing: {text}")

speech = sv.Speech(callback=printout, model="model", partial=True)
#Run blocking so script doesn't terminate (we're not doing anything else anyways)
speech.start(blocking=True)