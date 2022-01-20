# Simple-Vosk
A Python wrapper for simple offline real-time dictation (speech-to-text) and speaker-recognition using Vosk. Check out the official [Vosk GitHub page](https://github.com/alphacep/vosk-api) for the original API (documentation + support for other languages).

This module was created to make using a simple implementation of Vosk *very* quick and easy. It is intended for rapid prototyping and experimenting; not for production use.

For example, I used this module in a quick personal-assistant program.

## Features
* Uses Vosk: lightweight, multilingual, offline, and fast speech recognition.
* Runs in background thread (non-blocking).
* Both complete-sentence and real-time outputs.
* Optional speaker-recognition (using X-Vectors).
* Configurable filter-phrase list (eliminate common false outputs).

## Requirements
Should work with Python 3.6+. Tested with Python 3.8.7 on Windows 10 1903.

Python Modules: *(see `requirements.txt`)*
* vosk
* sounddevice
* numpy

You will also need to download Vosk models; one for your language of choice, and (if desired) the speaker-recognition model. Both can be found on the [Vosk models page](https://alphacephei.com/vosk/models). If you don't use speaker recognition, you only need the one model.

## Examples
This repository contains some examples of usage; `ExampleSimpleDictation.py`, `ExampleSpeakerRecognition.py`, and `ExampleNonBlocking.py`. Check the [Documentation.md file](https://github.com/Kenneract/Simple-Vosk/Documentation.md) for more in-depth info.

Below is the simplest implementation to get a fully-functioning speech-recognition system.
``` python
import simpleVosk as sv

def prnt(txt, spk, full):
	print(txt)

s = sv.Speech(callback=prnt, model="model")
s.run(blocking=True)
```

## Troubleshooting
Make sure your default input device is working, and/or ensure you are passing the correct `DeviceID` to the `Speech` object. You can see device IDs with the `listDevices()` method in `simpleVosk.py`.

Make sure you have Windows microphone access enabled. Having this disabled can cause errors similar to this: `sounddevice.PortAudioError: Error opening RawInputStream: Unanticipated host error [PaErrorCode -9999]: 'Undefined external error.' [MME error 1]`

## A Note on Conventions
This project goes against some standard Python conventions:
* It uses camelCase for naming methods (and files) rather than snake_case
* Tabs are used rather than 4 spaces for indentation (as I am a sane human being)
* Non-standard docstring formats are being used

## Future Plans
* Add ability to add custom words/phrases (KaldiRecognizer appears to only accept *replacement* dictionaries)
* Use proper docstrings