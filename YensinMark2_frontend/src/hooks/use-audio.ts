import { useState, useCallback } from 'react';
import { ElevenLabsService, IAudioService } from '../services/audio';
import { AudioConfig } from '../config/audio';

export function useAudio() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioService] = useState<IAudioService>(() => 
    new ElevenLabsService({
      apiKey: AudioConfig.elevenLabs.apiKey,
      voiceId: AudioConfig.elevenLabs.voiceId,
      model: AudioConfig.elevenLabs.model,
    })
  );

  // Function to speak text using TTS
  const speakText = useCallback(async (text: string) => {
    if (!text) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const audioData = await audioService.textToSpeech(text);
      
      // Create and play audio
      const audioBlob = new Blob([audioData], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      // Clean up URL object after playing
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
      };
      
      await audio.play();
      return audio; // Return audio element for further control if needed
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(`Failed to convert text to speech: ${errorMessage}`);
      console.error('Text-to-speech error:', err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [audioService]);

  // Function to transcribe speech from audio blob
  const transcribeSpeech = useCallback(async (audioBlob: Blob) => {
    console.log('transcribeSpeech called with blob:', {
      size: audioBlob.size,
      type: audioBlob.type
    });
    
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Calling ElevenLabs API with audio service');
      const transcription = await audioService.speechToText(audioBlob);
      console.log('Received transcription:', transcription);
      return transcription;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(`Failed to transcribe speech: ${errorMessage}`);
      console.error('Speech-to-text error:', err);
      return '';
    } finally {
      setIsLoading(false);
    }
  }, [audioService]);

  return {
    speakText,
    transcribeSpeech,
    isLoading,
    error
  };
}
