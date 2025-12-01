from flask import Flask, render_template, jsonify, request, send_file
from gtts import gTTS
import os
import threading
import time
from datetime import datetime
import uuid
from buzzer import buzzer
import json
import speech_recognition as sr

app = Flask(__name__)

# Import the global buzzer instance from buzzer.py
# (already initialized there, no need to create a new one)

# Directory for storing audio files
AUDIO_DIR = 'static/audio'
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

# Bad words list (expandable) - using whole words to avoid false positives
BAD_WORDS = [
    'damn', 'hell', 'crap', 'stupid', 'idiot', 'fool', 'jerk', 'dumb',
    'shit', 'fuck', 'ass', 'bitch', 'bastard', 'piss', 'dick', 'pussy',
    'cock', 'whore', 'slut', 'fag', 'nigger', 'retard', 'cunt'
]

# Language options with voice variants and friendly names
LANGUAGES = {
    'en': {'name': 'English', 'voices': {
        'com': 'United States',
        'co.uk': 'United Kingdom', 
        'com.au': 'Australia',
        'co.in': 'India'
    }},
    'es': {'name': 'Spanish', 'voices': {
        'com': 'Default',
        'com.mx': 'Mexico',
        'es': 'Spain'
    }},
    'fr': {'name': 'French', 'voices': {
        'fr': 'France',
        'ca': 'Canada'
    }},
    'de': {'name': 'German', 'voices': {'de': 'Germany'}},
    'it': {'name': 'Italian', 'voices': {'it': 'Italy'}},
    'pt': {'name': 'Portuguese', 'voices': {
        'com.br': 'Brazil',
        'pt': 'Portugal'
    }},
    'ru': {'name': 'Russian', 'voices': {'ru': 'Russia'}},
    'ja': {'name': 'Japanese', 'voices': {'co.jp': 'Japan'}},
    'ko': {'name': 'Korean', 'voices': {'co.kr': 'Korea'}},
    'zh-CN': {'name': 'Chinese (Simplified)', 'voices': {'com': 'China'}},
    'zh-TW': {'name': 'Chinese (Traditional)', 'voices': {'com.tw': 'Taiwan'}},
    'ar': {'name': 'Arabic', 'voices': {'com': 'Default'}},
    'hi': {'name': 'Hindi', 'voices': {'co.in': 'India'}},
    'nl': {'name': 'Dutch', 'voices': {'nl': 'Netherlands'}},
    'pl': {'name': 'Polish', 'voices': {'pl': 'Poland'}},
    'tr': {'name': 'Turkish', 'voices': {'com.tr': 'Turkey'}},
}

# Speech rate options (slow=True for slow, slow=False for normal)
SPEECH_RATES = {
    'slow': {'value': True, 'label': 'Slow'},
    'normal': {'value': False, 'label': 'Normal'}
}

# Activity log for dashboard
activity_log = []
max_log_entries = 50

def check_bad_words(text):
    """Check if text contains bad words (using word boundaries to avoid false positives)"""
    import re
    text_lower = text.lower()
    found_words = []
    
    for bad_word in BAD_WORDS:
        # Use word boundaries to match whole words only
        pattern = r'\b' + re.escape(bad_word) + r'\b'
        if re.search(pattern, text_lower):
            found_words.append(bad_word)
    
    return found_words

def log_activity(action, details):
    """Log activity to dashboard"""
    global activity_log
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'details': details
    }
    
    activity_log.insert(0, log_entry)
    
    # Keep only the last max_log_entries
    if len(activity_log) > max_log_entries:
        activity_log = activity_log[:max_log_entries]

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html', 
                         languages=LANGUAGES,
                         speech_rates=SPEECH_RATES)

@app.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text', '').strip()
        language = data.get('language', 'en')
        voice = data.get('voice', 'com')
        speed = data.get('speed', 'normal')
        volume = data.get('volume', 100)  # 0-100
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Check for bad words
        bad_words_found = check_bad_words(text)
        warning = None
        
        if bad_words_found:
            # Activate buzzer
            buzzer.beep(duration=2.0, pattern='warning')
            warning = f"Warning: Inappropriate language detected: {', '.join(bad_words_found)}"
            log_activity('Bad Words Detected', {
                'text': text[:50] + '...' if len(text) > 50 else text,
                'bad_words': bad_words_found,
                'language': language
            })
        
        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex[:8]}_{int(time.time())}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)
        
        # Convert speed parameter
        slow = SPEECH_RATES.get(speed, {}).get('value', False)
        
        # Generate TTS
        tld = voice if voice else 'com'
        tts = gTTS(text=text, lang=language, tld=tld, slow=slow)
        tts.save(filepath)
        
        # Log activity
        log_activity('Text to Speech', {
            'text': text[:50] + '...' if len(text) > 50 else text,
            'language': LANGUAGES.get(language, {}).get('name', language),
            'voice': voice,
            'speed': speed,
            'file': filename
        })
        
        # Don't auto-play - user will use play button instead
        
        return jsonify({
            'success': True,
            'audio_url': f'/static/audio/{filename}',
            'filename': filename,
            'warning': warning
        })
        
    except Exception as e:
        log_activity('Error', {'message': str(e)})
        return jsonify({'error': str(e)}), 500

# Global microphone instance (like Act7)
microphone = sr.Microphone()

@app.route('/api/voice-to-text', methods=['POST'])
def voice_to_text():
    """Convert voice input to text using USB microphone (Act7 style)"""
    try:
        data = request.json
        language = data.get('language', 'en')
        
        # Map language code to speech recognition format
        lang_map = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'it': 'it-IT',
            'pt': 'pt-PT',
            'ru': 'ru-RU',
            'ja': 'ja-JP',
            'ko': 'ko-KR',
            'zh-CN': 'zh-CN',
            'zh-TW': 'zh-TW',
            'ar': 'ar-SA',
            'hi': 'hi-IN',
            'nl': 'nl-NL',
            'pl': 'pl-PL',
            'tr': 'tr-TR'
        }
        
        recognition_lang = lang_map.get(language, 'en-US')
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Use USB microphone (Act7 style - simpler and more reliable)
        try:
            with microphone as source:
                log_activity('Listening', {'language': LANGUAGES.get(language, {}).get('name', language)})
                
                # Quick ambient noise adjustment (Act7 uses 0.5s)
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen with shorter timeout for better responsiveness (Act7 uses 5s)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except OSError as e:
            log_activity('Error', {'message': f'Microphone not found: {str(e)}'})
            return jsonify({'error': 'Could not find PyAudio; check installation. Make sure your USB microphone is connected.'}), 500
        
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio, language=recognition_lang)
        
        log_activity('Voice Recognized', {
            'text': text,
            'language': LANGUAGES.get(language, {}).get('name', language)
        })
        
        # Check for bad words
        bad_words_found = check_bad_words(text)
        warning = None
        
        if bad_words_found:
            buzzer.beep(duration=2.0, pattern='warning')
            warning = f"Warning: Inappropriate language detected: {', '.join(bad_words_found)}"
        
        return jsonify({
            'success': True,
            'text': text,
            'warning': warning
        })
        
    except sr.WaitTimeoutError:
        return jsonify({'error': 'No speech detected. Please try again.'}), 400
    except sr.UnknownValueError:
        return jsonify({'error': 'Could not understand audio. Please speak clearly.'}), 400
    except sr.RequestError as e:
        return jsonify({'error': f'Speech recognition service error: {str(e)}'}), 500
    except Exception as e:
        log_activity('Error', {'message': str(e)})
        return jsonify({'error': str(e)}), 500

@app.route('/api/activity-log', methods=['GET'])
def get_activity_log():
    """Get activity log for dashboard"""
    return jsonify({'log': activity_log})

@app.route('/api/download/<filename>', methods=['GET'])
def download_audio(filename):
    """Download audio file"""
    try:
        filepath = os.path.join(AUDIO_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-buzzer', methods=['POST'])
def test_buzzer():
    """Test buzzer functionality"""
    try:
        buzzer.beep(duration=0.5, pattern='single')
        log_activity('Buzzer Test', {'result': 'Success'})
        return jsonify({'success': True, 'message': 'Buzzer tested successfully'})
    except Exception as e:
        log_activity('Buzzer Test', {'result': 'Failed', 'error': str(e)})
        return jsonify({'error': str(e)}), 500

def play_audio(filepath):
    """Play audio file on Raspberry Pi"""
    try:
        # Use mpg123 or omxplayer to play audio
        os.system(f'mpg123 -q "{filepath}" 2>/dev/null || omxplayer -o local "{filepath}" 2>/dev/null')
    except Exception as e:
        print(f"Error playing audio: {e}")

@app.route('/api/cleanup-old-files', methods=['POST'])
def cleanup_old_files():
    """Clean up old audio files (older than 1 hour)"""
    try:
        current_time = time.time()
        deleted_count = 0
        
        for filename in os.listdir(AUDIO_DIR):
            filepath = os.path.join(AUDIO_DIR, filename)
            
            # Check if file is older than 1 hour
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > 3600:  # 1 hour
                    os.remove(filepath)
                    deleted_count += 1
        
        log_activity('Cleanup', {'files_deleted': deleted_count})
        return jsonify({'success': True, 'deleted': deleted_count})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 Mini-Bot Text-to-Speech System Starting...")
    print("=" * 60)
    print(f"✓ Buzzer initialized on GPIO 17")
    print(f"✓ Audio directory: {AUDIO_DIR}")
    print(f"✓ Supported languages: {len(LANGUAGES)}")
    print(f"✓ Bad words filter: {len(BAD_WORDS)} words")
    print("=" * 60)
    
    # use_reloader=False prevents GPIO conflicts on restart
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
