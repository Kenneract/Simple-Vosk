# SimpleVosk Documentation

## Generic
`simpleVosk.listDevices()`
Lists all available input devices.

___

## Class: Speech
**Constructor:**

`callback`
Function to call when voice data is processed. Must accept arguments (text:str,speakerName:str,isFull:bool). See the "simpleCallback" method.

`partial:bool` *(default=False)*
If True, will run the callback in real-time as text is processed as the speaker is talking. This allows for faster response times, but accuracy is lower and speaker-recognition is not available.

`model:str`
Path to the Vosk model.

`speakModel:str`
Path to the speaker-recognition Vosk model. (Optional; passing None disables speaker recognition)

`signatures:dict`
Dict of {"Speaker":[X-Vector]} speaker-signature pairs.

`maxSpeakThresh:float` *(default=0.55)*
The maximum cosine distance to accept a voice signature match. Smaller values mean tighter tolerances.

`filterText:bool` *(default=True)*
If should filter common false-triggers from running the callback (ex. Vosk sometimes pulls a "huh" from silence)

`printUnknownSigs:bool` *(default=True)*
If unreogniced speaker signatures (X-Vectors) should be printed to console (good for setting up new signatures).

`deviceID:int` *(default=None)*
The device number from listDevices(). None appears to use the system-default device.

`verbose:bool` *(default=False)*
If should print debug data (such as voice signature x-vector distances)

**Methods:**

`Speech.run(blocking:bool=False)`
Begins speech recognition. If `blocking` is `False`, Vosk will run in a background thread and not block execution.

`Speech.stop()`
Stops ongoing speech recognition.

`Speech.isRunning()`
Returns `True` if speech recognition is running, `False` otherwise.

`Speech.addFilterWords(words:list)`
Accepts a list of words/phrases to be ignored. Intended to reduce false-triggers (ex. Vosk sometimes interprets a "huh" from silence). Only used when `filterText` is `True`.