import logging
from typing import Optional
import os
import platform
import tempfile
from gtts import gTTS

class AudioOutput:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.system = platform.system()  # Get OS type
        print(self.system)
        
        try:   
            print("Initializing Google Text-to-Speech engine...")
            self.logger.info("Initializing Google Text-to-Speech engine...")
            
            # Configure TTS settings
            self.lang = config.get('language', 'en')
            self.slow_mode = config.get('slow', False)
            
            # Test the engine
            self._test_engine()
            self.logger.info("✓ Text-to-speech engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize text-to-speech: {str(e)}")
            raise RuntimeError("Text-to-speech initialization failed") from e
    
    def _test_engine(self) -> None:
        """Test the TTS engine with a simple phrase"""
        try:
            self.speak("Starting System")
        except Exception as e:
            raise RuntimeError(f"TTS engine test failed: {str(e)}")
    
    def _play_audio(self, file_path: str) -> None:
        """Play audio file based on OS"""
        try:
            # Verify file exists and has size
            if not os.path.exists(file_path):
                self.logger.error(f"Audio file not found: {file_path}")
                return
            if os.path.getsize(file_path) == 0:
                self.logger.error(f"Audio file is empty: {file_path}")
                return
                
            self.logger.debug(f"Playing audio file: {file_path} ({os.path.getsize(file_path)} bytes)")
            
            if self.system == "Darwin":  # macOS
                os.system(f"afplay {file_path} 2>/dev/null")
            elif self.system == "Linux":
                # Added --quiet flag and -q for better playback
                os.system(f"mpg321 {file_path} >/dev/null 2>&1")
            elif self.system == "Windows":
                os.system(f"start {file_path}")
            else:
                self.logger.error(f"Unsupported operating system: {self.system}")
                
            # Verify the play command worked
            if os.system("which mpg321 >/dev/null 2>&1") != 0 and self.system == "Linux":
                self.logger.error("mpg321 not installed. Please install with: sudo apt-get install mpg321")
                
        except Exception as e:
            self.logger.error(f"Error playing audio: {str(e)}")
    
    def speak(self, text: str) -> None:
        """Convert text to speech using Google TTS"""
        if not text:
            return
            
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                temp_filename = fp.name
            
            # Generate speech
            tts = gTTS(text=text, 
                      lang=self.lang,
                      slow=self.slow_mode)
            tts.save(temp_filename)
            
            # Play the audio
            self._play_audio(temp_filename)
            
            # Clean up
            os.unlink(temp_filename)
            
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {str(e)}")
    
    def change_language(self, language_code: str) -> None:
        """Change TTS language"""
        try:
            self.lang = language_code
            self.logger.info(f"Changed TTS language to: {language_code}")
        except Exception as e:
            self.logger.error(f"Error changing language: {str(e)}")
    
    def toggle_slow_mode(self) -> None:
        """Toggle slow pronunciation mode"""
        try:
            self.slow_mode = not self.slow_mode
            self.logger.info(f"Slow mode: {'enabled' if self.slow_mode else 'disabled'}")
        except Exception as e:
            self.logger.error(f"Error toggling slow mode: {str(e)}") 