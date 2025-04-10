
export interface Message {
  text: string;
  isUser: boolean;
  agent_name?: string;
  agent_type?: string;
  voice_text?: string; // Field for text to be used for speech synthesis
  display_images?: string[]; // Array of base64-encoded images
}

export interface BackendResponse {
  output: string;
  agent_name?: string;
  agent_type?: string;
  voice_text?: string; // For summarized response used in speech
  display_images?: string[]; // Array of base64-encoded images
}
