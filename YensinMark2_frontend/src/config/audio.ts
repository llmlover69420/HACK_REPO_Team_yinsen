// Audio service configuration

// Debug all environment variables
console.log('All environment variables:', import.meta.env);

// Get API key and voice ID from environment variables
const apiKey = import.meta.env.VITE_ELEVENLABS_API_KEY || '';
const voiceId = import.meta.env.VITE_ELEVENLABS_VOICE_ID || 'EXAVITQu4vr4xnSDxMaL';

// Debug the specific variables we need
console.log('ElevenLabs API Key:', apiKey ? `${apiKey.substring(0, 5)}...${apiKey.substring(apiKey.length - 4)}` : 'MISSING');
console.log('ElevenLabs Voice ID:', voiceId);

// Check if API key looks valid
if (!apiKey) {
  console.error('ElevenLabs API key is missing!');
} else if (!apiKey.startsWith('sk_')) {
  console.warn('ElevenLabs API key format may be incorrect - should start with "sk_"');
}

export const AudioConfig = {
  // ElevenLabs configuration
  elevenLabs: {
    apiKey, // Add your API key here or in .env file
    voiceId, // Default voice ID
    model: 'eleven_multilingual_v2', // Default model
  },
  
  // Add other audio service configurations here if needed in the future
};

// Instructions for getting an ElevenLabs API key:
// 1. Create an account at https://elevenlabs.io
// 2. Go to your profile settings
// 3. Copy your API key
// 4. Add it to your .env file as REACT_APP_ELEVENLABS_API_KEY=your_api_key_here
