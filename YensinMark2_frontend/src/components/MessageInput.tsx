
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ArrowRight, Loader2 } from "lucide-react";
import { useState } from "react";
import SpeechInput from "./SpeechInput";

interface MessageInputProps {
  currentMessage: string;
  setCurrentMessage: (message: string) => void;
  handleSendMessage: (message: string) => void;
  isLoading: boolean;
}

const MessageInput = ({ 
  currentMessage, 
  setCurrentMessage, 
  handleSendMessage,
  isLoading
}: MessageInputProps) => {
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(currentMessage);
    }
  };

  return (
    <div className="p-5 border-t border-border bg-card sticky bottom-0 backdrop-blur-sm">
      <div className="flex flex-col gap-2 max-w-4xl mx-auto">
        {isLoading && (
          <div className="text-xs text-center text-primary animate-pulse">
            {/* Show more detailed status message when loading */}
            Connecting to AI backend... If this takes too long, the server might be unavailable or have CORS issues.
          </div>
        )}
        <div className="flex items-center gap-3">
          <Input
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type something..."
            className="flex-grow border-border bg-secondary/50 focus-visible:ring-primary/30"
            disabled={isLoading}
          />
          
          {/* Mic button */}
          <SpeechInput 
            onTranscription={(text) => setCurrentMessage(text)}
            disabled={isLoading}
          />
          
          {/* Send button */}
          <Button 
            onClick={() => handleSendMessage(currentMessage)}
            disabled={!currentMessage.trim() || isLoading}
            size="icon"
            className="bg-primary hover:bg-primary/90 transition-all"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowRight className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MessageInput;
