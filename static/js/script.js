// ===================================
// Global Variables
// ===================================
let currentAudioUrl = null;
let currentFilename = null;
let audioElement = document.getElementById('audioElement');
let isRecording = false;

// Web Speech API recognition instance (like Act7)
let recognition = null;

// ===================================
// DOM Elements
// ===================================
const textInput = document.getElementById('textInput');
const speakBtn = document.getElementById('speakBtn');
const voiceBtn = document.getElementById('voiceBtn');
const languageSelect = document.getElementById('languageSelect');
const voiceSelect = document.getElementById('voiceSelect');
const speedSelect = document.getElementById('speedSelect');
const volumeSlider = document.getElementById('volumeSlider');
const volumeValue = document.getElementById('volumeValue');
const testBuzzerBtn = document.getElementById('testBuzzerBtn');
const activityLog = document.getElementById('activityLog');
const refreshLogBtn = document.getElementById('refreshLogBtn');
const notification = document.getElementById('notification');
const loadingOverlay = document.getElementById('loadingOverlay');
const botMessage = document.getElementById('botMessage');
const currentLanguage = document.getElementById('currentLanguage');
const audioPlayer = document.getElementById('audioPlayer');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');
const downloadBtn = document.getElementById('downloadBtn');
const audioFilename = document.getElementById('audioFilename');
const voiceStatus = document.getElementById('voiceStatus');

// ===================================
// Event Listeners
// ===================================
document.addEventListener('DOMContentLoaded', function () {
  // Initialize
  updateVoiceOptions();
  loadActivityLog();

  // Text to Speech
  speakBtn.addEventListener('click', handleTextToSpeech);

  // Voice Input
  voiceBtn.addEventListener('click', handleVoiceInput);

  // Language change
  languageSelect.addEventListener('change', function () {
    updateVoiceOptions();
    updateCurrentLanguage();
  });

  // Volume slider
  volumeSlider.addEventListener('input', function () {
    volumeValue.textContent = this.value;
    audioElement.volume = this.value / 100;
  });

  // Test buzzer
  testBuzzerBtn.addEventListener('click', testBuzzer);

  // Refresh log
  refreshLogBtn.addEventListener('click', loadActivityLog);

  // Audio controls
  playBtn.addEventListener('click', playAudio);
  pauseBtn.addEventListener('click', pauseAudio);
  downloadBtn.addEventListener('click', downloadAudio);

  // Audio element events
  audioElement.addEventListener('play', function () {
    playBtn.style.display = 'none';
    pauseBtn.style.display = 'block';
  });

  audioElement.addEventListener('pause', function () {
    playBtn.style.display = 'block';
    pauseBtn.style.display = 'none';
  });

  audioElement.addEventListener('ended', function () {
    playBtn.style.display = 'block';
    pauseBtn.style.display = 'none';
  });

  // Keyboard shortcuts
  textInput.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'Enter') {
      handleTextToSpeech();
    }
  });

  // Auto-refresh log every 10 seconds
  setInterval(loadActivityLog, 10000);
});

// ===================================
// Text to Speech Functions
// ===================================
async function handleTextToSpeech() {
  const text = textInput.value.trim();

  if (!text) {
    showNotification('Please enter some text', 'error');
    return;
  }

  const language = languageSelect.value;
  const voice = voiceSelect.value;
  const speed = speedSelect.value;
  const volume = volumeSlider.value;

  showLoading(true);
  speakBtn.disabled = true;

  try {
    const response = await fetch('/api/text-to-speech', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text,
        language: language,
        voice: voice,
        speed: speed,
        volume: volume
      })
    });

    const data = await response.json();

    if (response.ok && data.success) {
      // Display warning if bad words detected
      if (data.warning) {
        showNotification(data.warning, 'warning');
      } else {
        showNotification('Speech generated successfully!', 'success');
      }

      // Update bot message
      updateBotMessage(text);

      // Show audio player
      currentAudioUrl = data.audio_url;
      currentFilename = data.filename;
      audioElement.src = currentAudioUrl;
      audioFilename.textContent = currentFilename;
      audioPlayer.style.display = 'block';

      // Set volume and auto-play audio
      audioElement.volume = volume / 100;
      audioElement.play();

      // Reload activity log
      loadActivityLog();

    } else {
      showNotification(data.error || 'Failed to generate speech', 'error');
    }

  } catch (error) {
    console.error('Error:', error);
    showNotification('An error occurred: ' + error.message, 'error');
  } finally {
    showLoading(false);
    speakBtn.disabled = false;
  }
}

// ===================================
// Voice Input Functions (Web Speech API - like Act7)
// ===================================

// Initialize Web Speech API
function initSpeechRecognition() {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function () {
      isRecording = true;
      voiceBtn.classList.add('listening');
      voiceBtn.innerHTML = '<i class="fas fa-stop"></i><span>Stop Listening</span>';
      voiceStatus.innerHTML = '<div class="status-message info">🎤 Listening... Speak now! (Auto-stops when you stop talking)</div>';
    };

    recognition.onend = function () {
      isRecording = false;
      voiceBtn.classList.remove('listening');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Speak to Mini-Bot</span>';
    };

    recognition.onresult = function (event) {
      const transcript = event.results[0][0].transcript;

      // Display recognized text in textbox
      textInput.value = transcript;
      voiceStatus.innerHTML = '<div class="status-message success">✓ Voice recognized successfully!</div>';

      // Update bot message
      updateBotMessage(transcript);

      // Check for bad words via server
      checkBadWordsAndNotify(transcript);

      // Reload activity log
      loadActivityLog();

      // Auto-clear status after 3 seconds
      setTimeout(() => {
        voiceStatus.innerHTML = '';
      }, 3000);
    };

    recognition.onerror = function (event) {
      console.error('Speech recognition error:', event.error);
      isRecording = false;
      voiceBtn.classList.remove('listening');
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i><span>Speak to Mini-Bot</span>';

      if (event.error === 'no-speech') {
        voiceStatus.innerHTML = '<div class="status-message error">✗ No speech detected. Please try again.</div>';
        showNotification('No speech detected. Please try again.', 'error');
      } else if (event.error === 'not-allowed') {
        voiceStatus.innerHTML = '<div class="status-message error">✗ Microphone access denied</div>';
        showNotification('Microphone access denied. Please allow microphone access.', 'error');
      } else if (event.error === 'aborted') {
        voiceStatus.innerHTML = '<div class="status-message warning">⚠ Listening stopped</div>';
      } else {
        voiceStatus.innerHTML = '<div class="status-message error">✗ Error: ' + event.error + '</div>';
        showNotification('Speech recognition error: ' + event.error, 'error');
      }
    };
  } else {
    voiceBtn.disabled = true;
    voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Speech not supported</span>';
    console.warn('Web Speech API not supported in this browser');
  }
}

// Check bad words and trigger buzzer if needed
async function checkBadWordsAndNotify(text) {
  try {
    const response = await fetch('/api/check-bad-words', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: text })
    });

    const data = await response.json();

    if (data.has_bad_words) {
      showNotification(data.warning, 'warning');
    } else {
      showNotification('Voice recognized: "' + text + '"', 'success');
    }
  } catch (error) {
    // Just show success if bad word check fails
    showNotification('Voice recognized: "' + text + '"', 'success');
  }
}

function handleVoiceInput() {
  if (!recognition) {
    showNotification('Speech recognition not supported in this browser', 'error');
    return;
  }

  if (isRecording) {
    recognition.stop();
  } else {
    // Set language for recognition
    const lang = languageSelect.value;
    const langMap = {
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
    };
    recognition.lang = langMap[lang] || 'en-US';
    recognition.start();
  }
}

// Initialize speech recognition on page load
document.addEventListener('DOMContentLoaded', function () {
  initSpeechRecognition();
});

// ===================================
// Audio Control Functions
// ===================================
function playAudio() {
  if (audioElement.src) {
    audioElement.play();
  }
}

function pauseAudio() {
  audioElement.pause();
}

function downloadAudio() {
  if (currentFilename) {
    window.location.href = '/api/download/' + currentFilename;
    showNotification('Downloading audio file...', 'info');
  }
}

// ===================================
// Activity Log Functions
// ===================================
async function loadActivityLog() {
  try {
    const response = await fetch('/api/activity-log');
    const data = await response.json();

    if (data.log && data.log.length > 0) {
      displayActivityLog(data.log);
    } else {
      activityLog.innerHTML = `
                <div class="log-empty">
                    <i class="fas fa-inbox"></i>
                    <p>No activity yet</p>
                </div>
            `;
    }

  } catch (error) {
    console.error('Error loading activity log:', error);
  }
}

function displayActivityLog(log) {
  let html = '';

  log.forEach(entry => {
    const className = entry.action.includes('Error') ? 'error' :
      entry.action.includes('Warning') || entry.action.includes('Bad Words') ? 'warning' : '';

    let detailsHtml = '';
    if (typeof entry.details === 'object') {
      detailsHtml = Object.entries(entry.details)
        .map(([key, value]) => {
          if (Array.isArray(value)) {
            value = value.join(', ');
          }
          return `<strong>${key}:</strong> ${value}`;
        })
        .join('<br>');
    } else {
      detailsHtml = entry.details;
    }

    html += `
            <div class="log-entry ${className}">
                <div class="log-header">
                    <span class="log-action">${entry.action}</span>
                    <span class="log-timestamp">${entry.timestamp}</span>
                </div>
                <div class="log-details">${detailsHtml}</div>
            </div>
        `;
  });

  activityLog.innerHTML = html;
}

// ===================================
// Helper Functions
// ===================================
function updateVoiceOptions() {
  const language = languageSelect.value;
  const voices = LANGUAGES_DATA[language]?.voices || { 'com': 'Default' };

  voiceSelect.innerHTML = '';

  // Handle both old array format and new object format
  if (Array.isArray(voices)) {
    voices.forEach(voice => {
      const option = document.createElement('option');
      option.value = voice;
      option.textContent = voice;
      voiceSelect.appendChild(option);
    });
  } else {
    // New format: object with voice code as key and country name as value
    Object.entries(voices).forEach(([voiceCode, countryName]) => {
      const option = document.createElement('option');
      option.value = voiceCode;
      option.textContent = countryName;
      voiceSelect.appendChild(option);
    });
  }
}

function updateCurrentLanguage() {
  const language = languageSelect.value;
  const languageName = LANGUAGES_DATA[language]?.name || 'English';
  currentLanguage.innerHTML = `<i class="fas fa-language"></i> ${languageName}`;
}

function updateBotMessage(text) {
  botMessage.textContent = text;
}

function showNotification(message, type = 'info') {
  notification.textContent = message;
  notification.className = `notification ${type}`;
  notification.style.display = 'block';

  setTimeout(() => {
    notification.style.display = 'none';
  }, 5000);
}

function showLoading(show) {
  loadingOverlay.style.display = show ? 'flex' : 'none';
}

async function testBuzzer() {
  testBuzzerBtn.disabled = true;

  try {
    const response = await fetch('/api/test-buzzer', {
      method: 'POST'
    });

    const data = await response.json();

    if (response.ok && data.success) {
      showNotification('Buzzer test successful!', 'success');
    } else {
      showNotification(data.error || 'Buzzer test failed', 'error');
    }

    loadActivityLog();

  } catch (error) {
    console.error('Error:', error);
    showNotification('An error occurred: ' + error.message, 'error');
  } finally {
    setTimeout(() => {
      testBuzzerBtn.disabled = false;
    }, 1000);
  }
}

// ===================================
// Initialize on load
// ===================================
updateCurrentLanguage();
