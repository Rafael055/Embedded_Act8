# 🤖 Mini-Bot Text-to-Speech System

A comprehensive Flask-based web application for multilingual text-to-speech conversion with voice input capabilities, designed for Raspberry Pi with USB microphone integration and buzzer notifications for content filtering.

## ✨ Features

### Core Functionality
- **Text-to-Speech Conversion**: Convert written text to natural-sounding speech using gTTS (Google Text-to-Speech)
- **Voice Input**: Record speech through USB microphone and convert to text
- **Multilingual Support**: 16+ languages with multiple voice variants per language
- **Speech Rate Control**: Adjust between normal and slow speech rates
- **Volume Control**: Dynamic volume adjustment (0-100%)

### Advanced Features
- **Audio File Management**: Save and download generated audio files as MP3
- **Bad Word Detection**: Automatic profanity filter with buzzer notification
- **Hardware Integration**: Buzzer on GPIO 17 (same as Act6/Act7) for warning alerts
- **Activity Dashboard**: Real-time monitoring of all system activities
- **Multiple Voice Variants**: Select different accent/regional voices per language
- **Audio Playback**: Built-in audio player with play/pause/download controls

### User Interface
- **Modern Bot Design**: Animated robot avatar with floating effects
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Dark Theme**: Easy on the eyes with professional gradient backgrounds
- **Real-time Feedback**: Loading indicators, notifications, and status updates
- **Activity Log**: Comprehensive logging of all user interactions

## 🎯 Hardware Requirements

- **Raspberry Pi** (any model with GPIO support)
- **USB Microphone** (same as used in Act7)
- **Buzzer** connected to GPIO 17 (BCM mode)
- **Speakers** or audio output device (for audio playback)

## 📋 Software Requirements

- Python 3.7+
- Flask 2.3.3
- gTTS 2.3.2
- SpeechRecognition 3.10.0
- RPi.GPIO 0.7.1
- PyAudio 0.2.13
- mpg123 or omxplayer (for audio playback)

## 🚀 Installation

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip portaudio19-dev mpg123 flac
```

### 2. Create Virtual Environment (Recommended)

```bash
cd /home/pi/Documents/Embedded/Act8
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Hardware Setup

Connect the buzzer to GPIO 17 (BCM mode):
- Buzzer positive (+) → GPIO 17
- Buzzer negative (-) → Ground (GND)

Ensure your USB microphone is plugged in and recognized:
```bash
arecord -l  # List recording devices
```

## 🎮 Usage

### Starting the Application

```bash
cd /home/pi/Documents/Embedded/Act8
source .venv/bin/activate  # If using virtual environment
python app.py
```

The server will start on `http://0.0.0.0:5000`

Access from:
- Local: `http://localhost:5000`
- Network: `http://<raspberry-pi-ip>:5000`

### Using the Interface

#### Text-to-Speech
1. Select your desired language from the dropdown
2. Choose a voice variant (accent/region)
3. Set speech rate (slow/normal)
4. Adjust volume slider
5. Type your text in the text area
6. Click "Speak Text" button
7. Audio will play automatically and can be downloaded

#### Voice Input
1. Select the language you'll speak in
2. Click "Speak to Mini-Bot" button
3. Start speaking when "Listening..." appears
4. Your speech will be converted to text
5. Click "Speak Text" to hear it back

#### Buzzer Test
- Click "Test Buzzer" to verify buzzer functionality
- Buzzer will emit a short beep on GPIO 17

### Bad Word Detection
The system automatically detects inappropriate language and:
- Activates the buzzer with a warning pattern
- Displays a notification with detected words
- Logs the event in the activity dashboard

## 🌍 Supported Languages

- **English** (US, UK, Australia, India)
- **Spanish** (Spain, Mexico)
- **French** (France, Canada)
- **German**
- **Italian**
- **Portuguese** (Brazil, Portugal)
- **Russian**
- **Japanese**
- **Korean**
- **Chinese** (Simplified, Traditional)
- **Arabic**
- **Hindi**
- **Dutch**
- **Polish**
- **Turkish**

## 📁 Project Structure

```
Act8/
├── app.py                 # Main Flask application
├── buzzer.py             # Buzzer control module (GPIO 17)
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── static/
│   ├── audio/           # Generated audio files (auto-created)
│   ├── css/
│   │   └── style.css    # Stylesheet
│   ├── img/             # Images (optional)
│   └── js/
│       └── script.js    # Client-side JavaScript
└── templates/
    └── index.html       # Main HTML template
```

## 🔧 Configuration

### Bad Words List
Edit the `BAD_WORDS` list in `app.py` to customize the profanity filter:
```python
BAD_WORDS = [
    'word1', 'word2', 'word3'
]
```

### GPIO Pin
Change the buzzer GPIO pin in `app.py`:
```python
buzzer = Buzzer(pin=17)  # Change pin number here
```

### Audio Directory
Generated audio files are stored in `static/audio/` and automatically cleaned up after 1 hour.

## 🎨 Features Detail

### Activity Dashboard
- Real-time logging of all activities
- Timestamps for each event
- Color-coded entries (normal, warning, error)
- Auto-refresh every 10 seconds
- Manual refresh button

### Audio Management
- MP3 format for maximum compatibility
- Unique filenames to prevent conflicts
- Download button for saving files locally
- Auto-cleanup of old files (1+ hour)

### Buzzer Patterns
- **Single**: One continuous beep
- **Double**: Two short beeps
- **Triple**: Three short beeps
- **Warning**: Alternating beep pattern (for bad words)
- **Alarm**: Fast alternating pattern

## 🐛 Troubleshooting

### Microphone Issues
```bash
# Test microphone
arecord -d 5 test.wav
aplay test.wav

# Check if microphone is detected
arecord -l
```

### GPIO Permission Issues
```bash
sudo usermod -a -G gpio pi
sudo reboot
```

### Audio Playback Issues
```bash
# Install alternative audio player
sudo apt-get install mpg123 omxplayer
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 🔐 Security Note

The bad word filter is basic and can be bypassed. For production use:
- Implement more sophisticated content filtering
- Use external profanity detection APIs
- Add user authentication
- Implement rate limiting

## 📝 API Endpoints

- `GET /` - Main page
- `POST /api/text-to-speech` - Convert text to speech
- `POST /api/voice-to-text` - Convert voice to text
- `GET /api/activity-log` - Get activity log
- `GET /api/download/<filename>` - Download audio file
- `POST /api/test-buzzer` - Test buzzer
- `POST /api/cleanup-old-files` - Clean old audio files

## 🤝 Integration with Act6 & Act7

This project uses the same GPIO pin 17 configuration as:
- **Act6**: LED & Buzzer module for GPS notifications
- **Act7**: LED controller for voice commands

The buzzer can be shared between projects if properly managed.

## 📄 License

This project is for educational purposes. gTTS uses Google's text-to-speech API which requires internet connection.

## 🎉 Enjoy Your Mini-Bot!

Your talking mini-bot is now ready to speak in multiple languages! Feel free to customize and expand the functionality.
