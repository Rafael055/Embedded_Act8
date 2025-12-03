from gpiozero import Buzzer as GPIOBuzzer
import threading
import time

class Buzzer:
    def __init__(self, pin=17):
        """
        Initialize Buzzer module using gpiozero
        
        Args:
            pin: GPIO pin number (BCM mode) for Buzzer
        """
        self.pin = pin
        self.is_active = False
        self.thread = None
        
        # Setup using gpiozero
        self.buzzer = GPIOBuzzer(self.pin)
        
        print(f"✓ Buzzer initialized on GPIO {self.pin}")
    
    def beep(self, duration=1.0, pattern='single'):
        """
        Activate buzzer with different patterns
        
        Args:
            duration: Total duration in seconds
            pattern: 'single', 'double', 'triple', 'warning', 'alarm'
        """
        if self.is_active:
            return
        
        self.is_active = True
        
        if pattern == 'single':
            self._single_beep(duration)
        elif pattern == 'double':
            self._double_beep(duration)
        elif pattern == 'triple':
            self._triple_beep(duration)
        elif pattern == 'warning':
            self._warning_beep(duration)
        elif pattern == 'alarm':
            self._alarm_beep(duration)
        else:
            self._single_beep(duration)
        
        self.is_active = False
    
    def _single_beep(self, duration):
        """Single continuous beep"""
        self.buzzer.on()
        time.sleep(duration)
        self.buzzer.off()
    
    def _double_beep(self, duration):
        """Two short beeps"""
        beep_time = duration / 3
        gap_time = duration / 6
        
        self.buzzer.on()
        time.sleep(beep_time)
        self.buzzer.off()
        time.sleep(gap_time)
        self.buzzer.on()
        time.sleep(beep_time)
        self.buzzer.off()
    
    def _triple_beep(self, duration):
        """Three short beeps"""
        beep_time = duration / 5
        gap_time = duration / 10
        
        for i in range(3):
            self.buzzer.on()
            time.sleep(beep_time)
            self.buzzer.off()
            if i < 2:
                time.sleep(gap_time)
    
    def _warning_beep(self, duration):
        """Alternating beep pattern (warning)"""
        beep_time = 0.2
        gap_time = 0.1
        elapsed = 0
        
        while elapsed < duration:
            self.buzzer.on()
            time.sleep(beep_time)
            self.buzzer.off()
            time.sleep(gap_time)
            elapsed += (beep_time + gap_time)
    
    def _alarm_beep(self, duration):
        """Fast alternating beep pattern (alarm)"""
        beep_time = 0.1
        gap_time = 0.05
        elapsed = 0
        
        while elapsed < duration:
            self.buzzer.on()
            time.sleep(beep_time)
            self.buzzer.off()
            time.sleep(gap_time)
            elapsed += (beep_time + gap_time)
    
    def beep_async(self, duration=1.0, pattern='single'):
        """
        Activate buzzer asynchronously (non-blocking)
        """
        if self.thread and self.thread.is_alive():
            return
        
        self.thread = threading.Thread(target=self.beep, args=(duration, pattern))
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop buzzer and cleanup"""
        self.is_active = False
        self.buzzer.off()
    
    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.buzzer.off()
            self.buzzer.close()
        except:
            pass

# Global buzzer instance
buzzer = Buzzer()
