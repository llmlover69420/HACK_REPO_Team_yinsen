
import { useRef, useEffect, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Bot, 
  User, 
  Sparkles, // For orchestrator
  GraduationCap, // For study_manager
  DollarSign, // For finance_manager
  Stethoscope, // For health_manager
  Volume2, 
  VolumeX 
} from "lucide-react";
import { Message } from "@/types/message";
import DOMPurify from 'dompurify';
import { useAudio } from "@/hooks/use-audio";
import { Button } from "@/components/ui/button";

interface MessageAreaProps {
  messages: Message[];
  isLoading?: boolean;
}

interface AgentIconProps {
  agentName?: string;
  agentType?: string;
}

// Function to get avatar background color based on agent type
const getAvatarBackground = (agentType?: string): string => {
  if (!agentType) return "bg-gray-200 dark:bg-gray-700";
  
  const type = agentType.toLowerCase();
  
  // Color based on agent type
  switch (type) {
    case "orchestrator":
      return "bg-purple-100 dark:bg-purple-900/30";
    case "study_manager":
      return "bg-blue-100 dark:bg-blue-900/30";
    case "finance_manager":
      return "bg-green-100 dark:bg-green-900/30";
    case "health_manager":
      return "bg-red-100 dark:bg-red-900/30";
    default:
      return "bg-gray-200 dark:bg-gray-700";
  }
};

const AgentIcon = ({ agentType }: AgentIconProps) => {
  let imageSrc = "/images/Mia.jpg"; // Default to Mia (orchestrator)
  let altText = "Mia";
  
  if (agentType) {
    const type = agentType.toLowerCase();
    
    switch (type) {
      case "orchestrator":
        imageSrc = "/images/Mia.jpg";
        altText = "Mia";
        break;
      case "finance_manager":
        imageSrc = "/images/Flock.png";
        altText = "Flock";
        break;
      case "study_manager":
        imageSrc = "/images/Sara.png";
        altText = "Sara";
        break;
      case "health_manager":
        imageSrc = "/images/doctor.png";
        altText = "Doctor";
        break;
    }
  }
  
  return (
    <div className="relative" style={{ width: '6rem', height: '6rem' }}>
      <img 
        src={imageSrc} 
        alt={altText} 
        className="absolute inset-0 m-auto" 
        style={{ 
          maxWidth: '100%',
          maxHeight: '100%',
          width: 'auto',
          height: 'auto',
          borderRadius: '50%',
          objectPosition: 'center' 
        }}
      />
    </div>
  );
};

// Function removed - using the one defined above that doesn't rely on hardcoded agent names



const MessageArea = ({ messages, isLoading = false }: MessageAreaProps) => {
  const messageEndRef = useRef<HTMLDivElement>(null);
  const { speakText, isLoading: isSpeaking, error: audioError } = useAudio();
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Track already played messages using a stable fingerprint
  const playedMessagesRef = useRef(new Set<string>());
  
  // Store the last displayed message text to detect actual changes
  const lastDisplayedMessageRef = useRef<string>("");
  
  // Auto-scroll to the latest message
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);
  
  // Handle automatic audio playback for new messages
  useEffect(() => {
    // Don't process if no messages or loading
    if (messages.length === 0) return;
    
    // Get the last AI message that would be displayed
    const lastAiMessage = messages.filter(msg => !msg.isUser).pop();
    if (!lastAiMessage) return;
    
    // Create a stable fingerprint of this message that won't change between renders
    // We use text content hash to identify unique messages, not position or length
    const messageFingerprint = lastAiMessage.text.replace(/\s+/g, ' ').trim();
    
    // Check if this is actually a new message compared to what we last displayed
    // This is the critical check to avoid duplicate playback
    if (messageFingerprint === lastDisplayedMessageRef.current) {
      console.log("Same message still displayed, not playing audio again");
      return;
    }
    
    // Check if we've played this message before in this session
    if (playedMessagesRef.current.has(messageFingerprint)) {
      console.log("Already played this message before");
      return;
    }
    
    // Update our reference of the last displayed message
    lastDisplayedMessageRef.current = messageFingerprint;
    
    // Mark as played
    playedMessagesRef.current.add(messageFingerprint);
    
    console.log(`Playing new message: ${messageFingerprint.substring(0, 20)}...`);
    
    // Stop any currently playing audio first
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setCurrentlyPlaying(null);
    }
    
    // Play the audio with a small delay to let UI settle
    const textToSpeak = lastAiMessage.voice_text || lastAiMessage.text;
    
    // Skip empty messages
    if (!textToSpeak || textToSpeak.trim() === '') return;
    
    // Use longer delay (800ms) to ensure UI is completely ready
    const timer = setTimeout(() => {
      speakText(textToSpeak)
        .then(audio => {
          if (audio) {
            audioRef.current = audio;
            setCurrentlyPlaying(messageFingerprint);
            
            audio.onended = () => {
              setCurrentlyPlaying(null);
              audioRef.current = null;
            };
          }
        })
        .catch(error => {
          console.error('Failed to play audio:', error);
          setCurrentlyPlaying(null);
        });
    }, 800);
    
    return () => clearTimeout(timer);
  }, [messages, speakText]); // Depend on full messages array to catch actual message changes

  // Handle text-to-speech
  const handleSpeak = async (text: string, messageId: string) => {
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    
    if (currentlyPlaying === messageId) {
      setCurrentlyPlaying(null);
      return;
    }
    
    // Start new audio
    try {
      const audio = await speakText(text);
      if (audio) {
        audioRef.current = audio;
        setCurrentlyPlaying(messageId);
        
        audio.onended = () => {
          setCurrentlyPlaying(null);
          audioRef.current = null;
        };
      }
    } catch (error) {
      console.error('Failed to play audio:', error);
      setCurrentlyPlaying(null);
    }
  };

  // Show only the latest system response without the user's query
  return (
    <ScrollArea className="flex-grow">
      <div className="flex-grow p-4 overflow-y-auto bg-white dark:bg-gray-900 min-h-full">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center max-w-md p-6 rounded-lg bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm shadow-sm">
              <p className="text-gray-500 dark:text-gray-400">
                Type something below to start the conversation.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 animate-fade-in">
            {/* Show only the last AI message */}
            {(() => {
              // Get the last AI message (if any)
              const lastAiMessage = messages.filter(msg => !msg.isUser).pop();
              
              return (
                <>
                  {/* Only show the last AI message */}
                  {lastAiMessage && (
                    <div className="flex items-start gap-8">
                      {/* Agent icon and name */}
                      <div className="flex flex-col items-center">
                        <div>
                          <AgentIcon agentType={lastAiMessage.agent_type} />
                        </div>
                        {lastAiMessage.agent_name && (
                          <span className="text-sm font-medium text-gray-600 dark:text-gray-400 mt-2">
                            {lastAiMessage.agent_name}
                          </span>
                        )}
                      </div>
                      
                      {/* Message content positioned to align with the middle of the icon */}
                      <div className="flex flex-col flex-1" style={{ marginTop: '1rem' }}>
                        <div 
                          className="py-3 px-4 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-purple-100 dark:border-purple-900/30 rounded-tl-none flex-1 message-content"
                          dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(lastAiMessage.text) }}
                        />
                        
                        {/* Display base64-encoded images if available */}
                        {lastAiMessage.display_images && lastAiMessage.display_images.length > 0 && (
                          <div className="mt-3 space-y-3">
                            {lastAiMessage.display_images.map((imageData, index) => (
                              <div key={index} className="rounded-lg overflow-hidden border border-purple-100 dark:border-purple-900/30 shadow-sm">
                                <img 
                                  src={`data:image/jpeg;base64,${imageData}`}
                                  alt={`Generated image ${index + 1}`}
                                  className="w-full max-h-96 object-contain"
                                  onError={(e) => {
                                    (e.target as HTMLImageElement).style.display = 'none';
                                    console.error('Failed to load image', index);
                                  }}
                                />
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* Audio plays automatically - no button needed */}
                      </div>
                    </div>
                  )}
                  
                  {/* Show loading indicator when waiting for response */}
                  {isLoading && (
                    <div className="flex items-start gap-3">
                      <Avatar className="h-12 w-12 mt-1">
                        <AvatarFallback className="bg-purple-100 dark:bg-purple-900/30">
                          <Bot className="h-6 w-6 text-purple-600 dark:text-purple-300" />
                        </AvatarFallback>
                      </Avatar>
                      <div className="py-3 px-4 rounded-lg shadow-sm bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-purple-100 dark:border-purple-900/30 rounded-tl-none flex-1">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-75"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse delay-150"></div>
                          <span className="ml-2 text-sm text-gray-500">Processing your request...</span>
                        </div>
                      </div>
                    </div>
                  )}
                </>
              );
            })()}
            <div ref={messageEndRef} />
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

export default MessageArea;
