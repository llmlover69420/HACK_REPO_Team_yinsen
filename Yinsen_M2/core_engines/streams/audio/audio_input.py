import logging
import threading
import queue
#import pyaudio
import numpy as np
import time
import wave
import os
import tempfile
from typing import Optional, Dict, Callable
#import torch
from pathlib import Path
import sys
import openai  # Add OpenAI import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AudioInput:
    def __init__(self, config: dict, on_wake_word: Optional[Callable] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.running = False
        self.input_queue = queue.Queue()
        
        # Configure audio parameters directly from config
        self.channels = config.get('channels', 1)
        #self.format = pyaudio.paInt16
        self.chunk_size = config.get('chunk_size', 4096)  # Directly from config
        
        # Find a working input device and its supported sample rate
        self.device_index = config.get('device_index')
        self.sample_rate = config.get('sample_rate', 16000)
        
        #self.audio = pyaudio.PyAudio()
        
        # List available devices
        self.logger.info("Available audio devices:")
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            self.logger.info(f"Device {i}: {device_info['name']} (Input Channels: {device_info['maxInputChannels']})")
        
        # If no device specified, find a suitable one
        if self.device_index is None:
            self.device_index = self._find_working_device()
            
        if self.device_index is None:
            self.logger.error("No compatible audio input device found. Audio input will be disabled.")
            self.client = None  # Changed from self.model = None
            return
            
        # Audio processing parameters
        self.silence_threshold = config.get('silence_threshold', 300)  # Energy threshold
        self.silence_duration = config.get('silence_duration', 1.0)  # seconds
        
        # Wake word parameters
        self.wake_word = config.get('wake_word', "friday").lower()
        self.wake_word_enabled = config.get('wake_word_enabled', True)
        self.wake_word_threshold = config.get('wake_word_threshold', 0.5)
        self.listening_mode = False
        self.on_wake_word = on_wake_word  # Callback when wake word is detected
        
        # Audio state
        self.stream = None
        
        # Set up OpenAI client
        self._init_speech_recognizer()
        
        self.energy_callback = config.get('energy_callback', None)
        
        self.logger.info(f"Audio input initialized with device {self.device_index} at {self.sample_rate}Hz")
    
    def _find_working_device(self):
        """Find a working audio input device by testing each available device"""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Device supports input
                # Try common sample rates
                for rate in [16000, 44100, 48000, 8000]:  # Prefer 16kHz for Whisper
                    try:
                        self.logger.info(f"Testing device {i} ({device_info['name']}) at {rate}Hz...")
                        # Try to open a test stream to check if device works
                        test_stream = self.audio.open(
                            format=self.format,
                            channels=self.channels,
                            rate=rate,
                            input=True,
                            frames_per_buffer=self.chunk_size,
                            input_device_index=i,
                            start=False  # Don't actually start the stream
                        )
                        # If we got here, the device is compatible
                        test_stream.close()
                        self.sample_rate = rate
                        self.logger.info(f"Found working device {i}: {device_info['name']} at {rate}Hz")
                        return i
                    except Exception as e:
                        self.logger.debug(f"Device {i} not compatible at {rate}Hz: {e}")
                        continue
        return None
    
    def _init_speech_recognizer(self):
        """Initialize the OpenAI API client for Whisper"""
        try:
            # Get API key from config
            api_key = self.config.get('openai_api_key')
            
            # If API key not in config, try to get from environment variable
            if not api_key:
                api_key = os.environ.get('OPENAI_API_KEY')
                
            if not api_key:
                self.logger.error("OpenAI API key not found. Please set it in the config or as OPENAI_API_KEY environment variable.")
                self.client = None
                return
                
            # Set up the OpenAI client
            self.client = openai.OpenAI(api_key=api_key)
            self.logger.info("OpenAI API client initialized for Whisper transcription")
            
            # Set model configuration
            self.whisper_model = self.config.get('whisper_model', 'whisper-1')
            self.whisper_language = self.config.get('language', 'en')
            
            # Test the API connection
            self.logger.info("Testing OpenAI Whisper API connection...")
            # Just to check if client is configured correctly, no actual API call
            if self.client:
                self.logger.info("OpenAI client configuration successful")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            self.client = None
    
    def start(self):
        """Start the audio input listener"""
        if self.running or not self.client:
            return
            
        self.running = True
        
        # Start audio processing thread
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
        self.logger.info("Audio input listener started")
    
    def stop(self):
        """Stop the audio input listener"""
        self.running = False
        if hasattr(self, 'stream') and self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            
        if hasattr(self, 'audio'):
            self.audio.terminate()
            
        self.logger.info("Audio input listener stopped")
    
    def _is_speech(self, audio_data: bytes) -> bool:
        """Detect if audio chunk contains speech using energy levels."""
        # Calculate audio energy
        energy = sum(abs(int.from_bytes(audio_data[i:i+2], 'little', signed=True)) 
                    for i in range(0, len(audio_data), 2)) / len(audio_data)
        
        # Call energy callback if provided
        if self.energy_callback:
            self.energy_callback(energy)

        print(f"Energy: {energy}, Threshold: {self.silence_threshold}, {energy > self.silence_threshold}")
        
        # Return true if energy is above threshold
        return energy > self.silence_threshold
    
    def _check_for_wake_word(self, text):
        """Check if the wake word is in the recognized text"""
        if not text or not self.wake_word:
            return False
            
        # Convert everything to lowercase for comparison
        text = text.lower()
        print('Heard: ', text)
        
        # Simple check: wake word is in the text
        return self.wake_word in text
    
    def _save_audio_to_file(self, audio_data, filename):
        """Save audio data to a WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(audio_data))
    
    def _transcribe_audio(self, audio_file):
        """Transcribe audio using OpenAI Whisper API"""
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return ""
            
        try:
            # Open the audio file
            with open(audio_file, "rb") as file:
                # Call the OpenAI API
                response = self.client.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=file,
                    language=self.whisper_language,
                    response_format="text"
                )
                
                # The response is the transcription text
                return response.strip()
                
        except Exception as e:
            self.logger.error(f"Error transcribing audio with OpenAI API: {e}")
            return ""
    
    def _audio_loop(self):
        """Main audio processing loop"""
        buffer = []
        silent_chunks = 0
        voiced_chunks = 0
        was_speech = False
        
        try:
            # Open audio stream with robust error handling
            try:
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    frames_per_buffer=self.chunk_size,
                    input_device_index=self.device_index
                )
                
                self.logger.info("Audio stream opened, listening...")
            except Exception as e:
                self.logger.error(f"Failed to open audio stream: {e}")
                self.logger.error("Common causes: device is in use, incorrect permissions, or hardware issues")
                self.running = False
                return
            
            # For wake word detection, we need to periodically process chunks
            # to detect the wake word
            accumulated_audio = []
            last_process_time = time.time()
            
            while self.running:
                try:
                    # Read audio data with timeout to avoid blocking indefinitely
                    audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    
                    # If in wake word detection mode (not actively listening yet)
                    if not self.listening_mode and self.wake_word_enabled:
                        accumulated_audio.append(audio_data)
                        #print('Accumulated audio: ', len(accumulated_audio))
                        # Process accumulated audio every 1.5 seconds for wake word detection
                        current_time = time.time()
                        if current_time - last_process_time > 1.5 and len(accumulated_audio) > 0:
                            # Create temp file for the accumulated audio
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                                temp_filename = tmp_file.name
                            
                            # Save accumulated audio to temp file
                            self._save_audio_to_file(accumulated_audio, temp_filename)
                            
                            # Transcribe with Whisper
                            transcription = self._transcribe_audio(temp_filename)
                            
                            # Clean up temp file
                            os.unlink(temp_filename)
                            
                            # Reset accumulated audio and timer
                            accumulated_audio = []
                            last_process_time = current_time
                            
                            # If wake word detected in transcription
                            if transcription and self._check_for_wake_word(transcription):
                                self.logger.info(f"Wake word detected in: '{transcription}'")
                                self.listening_mode = True
                                
                                # Notify through callback
                                if self.on_wake_word:
                                    self.on_wake_word()
                                
                                # Reset for command recording
                                buffer = []
                                silent_chunks = 0
                                voiced_chunks = 0
                                was_speech = False
                    
                    # If in listening mode, record audio until silence is detected
                    elif self.listening_mode:
                        buffer.append(audio_data)
                        is_speech = self._is_speech(audio_data)
                        
                        # Track speech/silence for determining when to stop recording
                        if is_speech:
                            voiced_chunks += 1
                            silent_chunks = 0
                            was_speech = True
                        elif was_speech:
                            silent_chunks += 1
                        
                        # If enough silence after speech, process the recording
                        silence_time = silent_chunks * self.chunk_size / self.sample_rate
                        if was_speech and silence_time > self.silence_duration and voiced_chunks > 3:
                            self.logger.info("Processing command...")
                            
                            # Create a temporary file for the command audio
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                                command_audio_file = tmp_file.name
                            
                            # Save command audio to file
                            self._save_audio_to_file(buffer, command_audio_file)
                            
                            # Transcribe command with Whisper
                            command_text = self._transcribe_audio(command_audio_file)
                            
                            # Clean up temp file
                            os.unlink(command_audio_file)
                            
                            if command_text:
                                self.logger.info(f"Command recognized: {command_text}")
                                # Add recognized text to input queue
                                self.input_queue.put(command_text)
                            else:
                                self.logger.info("No command recognized")
                            
                            # Reset for next utterance
                            self.listening_mode = False
                            buffer = []
                            silent_chunks = 0
                            voiced_chunks = 0
                            was_speech = False
                    
                except IOError as e:
                    # Handle common IOErrors from PyAudio
                    self.logger.error(f"IOError in audio stream: {e}")
                    time.sleep(0.5)  # Prevent tight loop on errors
                    continue
                except Exception as e:
                    self.logger.error(f"Error processing audio: {e}")
                    time.sleep(0.5)
                    continue
            
        except Exception as e:
            self.logger.error(f"Error in audio loop: {e}")
            self.running = False
    
    def get_input(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get next voice input from queue"""
        try:
            return self.input_queue.get(block=timeout is not None, timeout=timeout)
        except queue.Empty:
            return None
    
    def is_listening(self):
        """Check if the system is in active listening mode"""
        return self.listening_mode 