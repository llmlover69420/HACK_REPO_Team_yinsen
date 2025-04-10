import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Mic, Square, Loader2 } from 'lucide-react';
import { useAudio } from '@/hooks/use-audio';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface SpeechInputProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

const SpeechInput = ({ onTranscription, disabled = false }: SpeechInputProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const { transcribeSpeech, isLoading, error } = useAudio();
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const [recordingTime, setRecordingTime] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    console.log('Starting recording...');
    try {
      // Reset state
      audioChunksRef.current = [];
      setRecordingTime(0);
      
      // Request microphone access with optimal settings for ElevenLabs
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 44100, // Higher sample rate for better quality
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });
      
      // Use the best format for ElevenLabs
      // Supported formats: .wav, .mp3, .m4a, etc.
      let options;
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        options = { mimeType: 'audio/wav' };
        console.log('Using WAV format');
      } else if (MediaRecorder.isTypeSupported('audio/mp3')) {
        options = { mimeType: 'audio/mp3' };
        console.log('Using MP3 format');
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options = { mimeType: 'audio/webm' };
        console.log('Using WebM format');
      } else {
        // Use default format if none of the above are supported
        options = {};
        console.log('Using default browser format');
      }
      
      console.log('Using audio format:', options.mimeType || 'default browser format');
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Request data at shorter intervals for more reliable recording
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log(`Audio chunk received: ${event.data.size} bytes`);
        }
      };
      
      // Set a timer to collect data every 250ms
      const dataInterval = setInterval(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.requestData();
        }
      }, 250);

      mediaRecorder.onstop = async () => {
        // Clear the data collection interval
        clearInterval(dataInterval);
        
        try {
          // Create blob with the correct MIME type (using the same type we selected earlier)
          const blobType = options.mimeType || 'audio/webm';
          const audioBlob = new Blob(audioChunksRef.current, { type: blobType });
          
          console.log('Audio recorded, size:', audioBlob.size, 'bytes');
          
          try {
            // Send to ElevenLabs for transcription using scribe_v1 model
            console.log('Sending audio to ElevenLabs for transcription using scribe_v1 model...');
            const transcription = await transcribeSpeech(audioBlob);
            
            if (transcription) {
              console.log('Transcription successful:', transcription);
              onTranscription(transcription);
            } else {
              // If we got an empty response, inform the user
              console.warn('Empty transcription received');
              onTranscription('(No speech detected)');
            }
          } catch (transcriptionError: any) {
            console.error('Transcription failed:', transcriptionError);
            
            // Check for specific error types and provide helpful messages
            let errorMsg = '';
            
            // Handle different error types
            if (transcriptionError.message) {
              errorMsg = transcriptionError.message;
              // Check if the error message contains an object representation
              if (errorMsg.includes('[object Object]')) {
                console.error('Error contains object:', transcriptionError);
                errorMsg = 'Invalid audio format or API configuration error';
              }
            } else {
              errorMsg = String(transcriptionError);
            }
            
            if (errorMsg.includes('format')) {
              // Audio format error
              console.log('Audio format error detected');
              onTranscription('Audio format not supported. Try recording again with a different browser.');
            } else if (errorMsg.includes('corrupt')) {
              // Corrupted audio
              console.log('Corrupted audio error detected');
              onTranscription('Audio recording corrupted. Please try again in a quieter environment.');
            } else if (errorMsg.includes('Authentication') || errorMsg.includes('API key')) {
              // API key issues
              console.log('API key error detected');
              onTranscription('ElevenLabs API key error. Please check your configuration.');
            } else if (errorMsg.includes('Rate limit')) {
              // Rate limiting
              console.log('Rate limit error detected');
              onTranscription('ElevenLabs rate limit reached. Please try again later.');
            } else if (errorMsg.includes('subscription')) {
              // Subscription issues
              console.log('Subscription error detected');
              onTranscription('Speech-to-text requires a paid ElevenLabs subscription');
            } else {
              // Generic error with status code if available
              const statusMatch = errorMsg.match(/status code (\d+)/);
              const statusCode = statusMatch ? statusMatch[1] : '';
              
              if (statusCode) {
                onTranscription(`Transcription failed (Error ${statusCode}). Please try again.`);
              } else {
                onTranscription('Could not transcribe speech. Please try again.');
              }
            }
          }
        } catch (error) {
          console.error('Transcription error:', error);
        } finally {
          // Stop all tracks to release the microphone
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    console.log('Stopping recording...');
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      console.log('MediaRecorder stopped');
      setIsRecording(false);
    } else {
      console.warn('Cannot stop recording - recorder not active');
    }
  };

  return (
    <div>
      <Button
        type="button"
        variant={isRecording ? "destructive" : "outline"}
        size="icon"
        disabled={disabled || isLoading}
        onClick={isRecording ? stopRecording : startRecording}
        className="rounded-full"
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording ? (
          <Square className="h-4 w-4" />
        ) : (
          <Mic className="h-4 w-4" />
        )}
      </Button>
      {error && <p className="text-red-500 text-xs mt-1">{error}</p>}
    </div>
  );
};

export default SpeechInput;
