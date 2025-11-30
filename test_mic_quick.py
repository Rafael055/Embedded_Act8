#!/usr/bin/env python3
"""Quick microphone test with Python 3.13 compatibility"""

import sys
import types

# Python 3.13+ compatibility
if sys.version_info >= (3, 13):
    aifc = types.ModuleType('aifc')
    audioop = types.ModuleType('audioop')
    
    audioop.error = Exception
    audioop.ratecv = lambda *args: (b'', 0)
    audioop.rms = lambda data, width: 0
    audioop.max = lambda data, width: 0
    audioop.minmax = lambda data, width: (0, 0)
    audioop.avg = lambda data, width: 0
    audioop.maxpp = lambda data, width: 0
    audioop.cross = lambda data, width: 0
    audioop.mul = lambda data, width, factor: data
    audioop.tomono = lambda data, width, lfactor, rfactor: data
    audioop.tostereo = lambda data, width, lfactor, rfactor: data
    audioop.add = lambda data1, data2, width: data1
    audioop.bias = lambda data, width, bias: data
    audioop.reverse = lambda data, width: data
    audioop.lin2lin = lambda data, width, newwidth: data
    audioop.lin2ulaw = lambda data, width: data
    audioop.ulaw2lin = lambda data, width: data
    audioop.lin2alaw = lambda data, width: data
    audioop.alaw2lin = lambda data, width: data
    audioop.lin2adpcm = lambda data, width, state: (data, state)
    audioop.adpcm2lin = lambda data, width, state: (data, state)
    
    sys.modules['aifc'] = aifc
    sys.modules['audioop'] = audioop

import speech_recognition as sr

print("🎤 Testing Microphone with Speech Recognition...")
print()

try:
    recognizer = sr.Recognizer()
    
    print("✓ SpeechRecognition initialized")
    print("✓ Starting microphone test...")
    print()
    print("Speak now (you have 5 seconds):")
    print()
    
    with sr.Microphone() as source:
        print("  Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("  ✓ Ready - Listening...")
        
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        print("  ✓ Audio captured!")
        print()
        
        print("  Recognizing speech...")
        text = recognizer.recognize_google(audio, language='en-US')
        
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"You said: \"{text}\"")
        print()
        
except sr.WaitTimeoutError:
    print("✗ No speech detected within timeout period")
    print("  Make sure your microphone is working and speak louder")
except sr.UnknownValueError:
    print("✗ Could not understand audio")
    print("  Try speaking more clearly")
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"  Type: {type(e).__name__}")
