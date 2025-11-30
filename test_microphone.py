#!/usr/bin/env python3
"""
Microphone Test Script for Mini-Bot TTS System
This script helps diagnose microphone issues
"""

import sys
import os

print("=" * 60)
print("🎤 Mini-Bot Microphone Diagnostic Tool")
print("=" * 60)
print()

# Test 1: Check if PyAudio is available
print("Test 1: Checking PyAudio installation...")
try:
    import pyaudio
    print("✓ PyAudio is installed")
    pa = pyaudio.PyAudio()
    print(f"✓ PyAudio version: {pyaudio.__version__}")
except ImportError:
    print("✗ PyAudio is NOT installed")
    print("  Install with: sudo apt-get install python3-pyaudio")
    sys.exit(1)
except Exception as e:
    print(f"✗ PyAudio error: {e}")
    sys.exit(1)

# Test 2: List all audio devices
print("\nTest 2: Listing audio devices...")
try:
    device_count = pa.get_device_count()
    print(f"✓ Found {device_count} audio devices:")
    print()
    
    for i in range(device_count):
        info = pa.get_device_info_by_index(i)
        print(f"  Device {i}: {info['name']}")
        print(f"    - Max Input Channels: {info['maxInputChannels']}")
        print(f"    - Max Output Channels: {info['maxOutputChannels']}")
        print(f"    - Default Sample Rate: {info['defaultSampleRate']}")
        print()
    
    pa.terminate()
except Exception as e:
    print(f"✗ Error listing devices: {e}")
    pa.terminate()
    sys.exit(1)

# Test 3: Check SpeechRecognition
print("\nTest 3: Checking SpeechRecognition...")
try:
    import speech_recognition as sr
    print("✓ SpeechRecognition is installed")
    print(f"✓ Version: {sr.__version__}")
except ImportError:
    print("✗ SpeechRecognition is NOT installed")
    print("  Install with: pip install SpeechRecognition")
    sys.exit(1)

# Test 4: List microphones via SpeechRecognition
print("\nTest 4: Listing microphones via SpeechRecognition...")
try:
    mic_list = sr.Microphone.list_microphone_names()
    print(f"✓ Found {len(mic_list)} microphone(s):")
    for i, name in enumerate(mic_list):
        print(f"  {i}: {name}")
except Exception as e:
    print(f"✗ Error listing microphones: {e}")

# Test 5: Try to initialize default microphone
print("\nTest 5: Testing default microphone...")
try:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("✓ Default microphone initialized successfully")
        print("  Adjusting for ambient noise (this takes a moment)...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✓ Ambient noise adjustment complete")
        print("  Microphone is ready to use!")
except OSError as e:
    print(f"✗ OSError: {e}")
    print("  This usually means PyAudio can't find a microphone")
    print("  Make sure your USB microphone is plugged in")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Check ALSA devices
print("\nTest 6: Checking ALSA recording devices...")
os.system("arecord -l 2>/dev/null || echo '  Run: arecord -l'")

print("\n" + "=" * 60)
print("Diagnostic Complete!")
print("=" * 60)
print()
print("If you see errors above:")
print("1. Make sure USB microphone is plugged in")
print("2. Run: arecord -l  (to see hardware devices)")
print("3. Run: sudo apt-get install python3-pyaudio")
print("4. Try a different USB port")
print("5. Reboot the Raspberry Pi")
print()
