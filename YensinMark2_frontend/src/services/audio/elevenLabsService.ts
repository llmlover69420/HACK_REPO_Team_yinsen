import axios from 'axios';

type AudioConfig = {
  apiKey: string;
  voiceId?: string;
  model?: string;
};

export class ElevenLabsService {
  private config: AudioConfig;

  constructor(config: AudioConfig) {
    this.config = config;
    console.log('ElevenLabs service initialized with voice ID:', config.voiceId);
  }

  // Text-to-Speech functionality (confirmed working with ElevenLabs API)
  async textToSpeech(text: string): Promise<ArrayBuffer> {
    try {
      console.log(`Converting text to speech using voice ID: ${this.config.voiceId}`);
      
      const response = await axios.post(
        `https://api.elevenlabs.io/v1/text-to-speech/${this.config.voiceId}`,
        { 
          text,
          model_id: this.config.model || 'eleven_multilingual_v2'
        },
        {
          headers: {
            'xi-api-key': this.config.apiKey,
            'Content-Type': 'application/json',
          },
          responseType: 'arraybuffer'
        }
      );
      
      console.log('TTS successful, received audio data of size:', response.data.byteLength);
      return response.data;
    } catch (error) {
      console.error('ElevenLabs TTS error:', error);
      throw error;
    }
  }

  // Speech-to-Text functionality using ElevenLabs API with scribe-v1 model
  async speechToText(audioBlob: Blob): Promise<string> {
    try {
      console.log(`Attempting speech-to-text with ${audioBlob.size} bytes of ${audioBlob.type} audio`);
      
      // Create form data with the required parameters
      const formData = new FormData();
      
      // Add the audio file - ElevenLabs expects 'file' as the field name based on sample code
      formData.append('file', audioBlob);
      
      // Use scribe_v1 as the official ElevenLabs STT model (with underscore, not hyphen)
      formData.append('model_id', 'scribe_v1');
      
      // Specify English language only
      formData.append('language_code', 'eng');
      
      // Log detailed information about the audio blob
      console.log('Audio blob details:', {
        type: audioBlob.type,
        size: audioBlob.size
      });
      
      // Log FormData entries for debugging
      console.log('FormData entries:', [...formData.entries()].map(entry => {
        if (entry[1] instanceof Blob) {
          return `${entry[0]}: Blob(${(entry[1] as Blob).size} bytes, ${(entry[1] as Blob).type})`;
        }
        return `${entry[0]}: ${String(entry[1])}`;
      }));
      
      console.log('Sending STT request to ElevenLabs API with scribe_v1 model');
      
      // Debug the API key (safely)
      console.log('Using API key:', this.config.apiKey ? 
        `${this.config.apiKey.substring(0, 5)}...${this.config.apiKey.substring(this.config.apiKey.length - 4)}` : 
        'MISSING API KEY');
      
      // Make the API request
      const response = await axios.post(
        'https://api.elevenlabs.io/v1/speech-to-text',
        formData,
        {
          headers: {
            'xi-api-key': this.config.apiKey
          },
          timeout: 30000 // 30 second timeout
        }
      );
      
      console.log('STT response:', response.data);
      
      // Extract the transcribed text from the response
      if (response.data && response.data.text) {
        return response.data.text;
      }
      
      return '';
    } catch (error: any) {
      // Provide detailed error information
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const data = error.response?.data;
        
        console.error('ElevenLabs STT API error:', {
          status,
          statusText: error.response?.statusText,
          data,
          message: error.message
        });
        
        // Handle specific error codes
        if (status === 400) {
          console.error('Bad request (400) details:', data);
          
          // Dump the full error response for debugging
          console.error('Full 400 error response:', JSON.stringify(error.response, null, 2));
          
          // Check for common issues
          if (data && typeof data === 'object') {
            if ('detail' in data) {
              // Convert object to string if needed
              const detailStr = typeof data.detail === 'object' 
                ? JSON.stringify(data.detail) 
                : String(data.detail);
              throw new Error(`ElevenLabs API error: ${detailStr}`);
            }
          }
          
          // Try to extract useful information from the error
          const errorMessage = typeof data === 'string' ? data : 
                             (data && typeof data === 'object' && 'message' in data) ? data.message : 
                             'Audio format may be incompatible or corrupted. Try a different recording format.';
          
          throw new Error(`ElevenLabs API error (400): ${errorMessage}`);
        } else if (status === 401 || status === 403) {
          throw new Error('Authentication failed. Please check your ElevenLabs API key.');
        } else if (status === 429) {
          throw new Error('Rate limit exceeded. Please try again later.');
        }
      }
      
      console.error('ElevenLabs STT error:', error);
      throw error;
    }
  }
}

export type IAudioService = {
  textToSpeech: (text: string) => Promise<ArrayBuffer>;
  speechToText: (audioBlob: Blob) => Promise<string>;
};