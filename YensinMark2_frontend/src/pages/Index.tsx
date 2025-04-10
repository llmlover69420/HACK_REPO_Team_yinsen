import { useState, useEffect } from "react";
import CalendarSection from "@/components/CalendarSection";
import LogsSection from "@/components/LogsSection";
import MessageArea from "@/components/MessageArea";
import YoutubeSection from "@/components/YoutubeSection";
import MessageInput from "@/components/MessageInput";
import ServerDebug from "@/components/ServerDebug";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight, Youtube } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Message, BackendResponse } from "@/types/message";

const Index = () => {
  const [currentMessage, setCurrentMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const { toast } = useToast();
  
  // Determine server URL based on environment variable
  const serverMode = import.meta.env.VITE_SERVER_MODE || 'main';
  const serverUrl = serverMode === 'test' ? 'http://localhost:8000' : 'http://51.21.162.46:8000';
  
  // Log the server mode and URL on component mount
  useEffect(() => {
    console.log('%c SERVER CONFIG ', 'background: #222; color: #bada55; font-size: 16px;');
    console.log(`Mode: ${serverMode}`);
    console.log(`API URL: ${serverUrl}`);
    console.log('%c -------------- ', 'background: #222; color: #bada55; font-size: 16px;');
  }, [serverMode, serverUrl]);

  const mockResponses: BackendResponse[] = [
    { output: "I'm sorry, I can't connect to the backend right now. This is a fallback response.", agent_name: "Mia" },
    { output: "The backend seems to be offline. Here's a simulated response instead.", agent_name: "Flock" },
    { output: "I'm currently running in offline mode. In a real scenario, I would fetch responses from the backend.", agent_name: "Doctor" },
    { output: `Backend connection failed. Try running the server at ${serverUrl} for actual AI responses.`, agent_name: "Sara" },
    { output: "This is a placeholder message. Please ensure your backend server is running for real responses.", agent_name: "Mia" }
  ];

  const getRandomMockResponse = () => {
    return mockResponses[Math.floor(Math.random() * mockResponses.length)];
  };

  const processMessageWithBackend = async (userMessage: string) => {
    setIsLoading(true);
    try {
      console.log("Sending message to backend:", userMessage);
      console.log(`%c Using API endpoint: ${serverUrl}/process-text`, 'color: #4CAF50; font-weight: bold;');
      const controller = new AbortController();
      // Increase timeout from 10 seconds to 60 seconds to give the backend more time to process
      const timeoutId = setTimeout(() => controller.abort(), 60000);

      const response = await fetch(`${serverUrl}/process-text`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: userMessage }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text().catch(() => "");
        console.error("Error response:", errorText);
        throw new Error(`Server responded with status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log("Received data from backend:", data);
      
      // Process the response from your backend
      console.log("Response format check:", data);
      
      // Based on actual backend response format seen in logs
      if (data.final_response_to_user) {
        // New format with direct fields
        return {
          output: data.final_response_to_user,
          agent_name: data.current_agent_name || "Mia",
          agent_type: data.current_agent_type || "orchestrator",
          voice_text: data.summarized_response || "",
          display_images: data.display_images || []
        };
      } else if (data.output && typeof data.output === 'object') {
        // If output is nested
        return {
          output: data.output.final_response_to_user || data.output.response || "",
          agent_name: data.output.current_agent_name || "Mia",
          agent_type: data.output.current_agent_type || "orchestrator",
          voice_text: data.output.summarized_response || "",
          display_images: data.output.display_images || []
        };
      } else {
        // Fallback to basic format
        return { 
          output: data.output || "", 
          agent_name: "Mia",
          agent_type: "orchestrator",
          voice_text: typeof data.output === 'string' ? data.output.replace(/<[^>]*>/g, '') : "",
          display_images: []
        };
      }
    } catch (error) {
      console.error("Error processing message:", error);

      let errorDescription = "Could not connect to the AI backend. Using fallback response instead.";

      if (error instanceof TypeError && error.message === "Failed to fetch") {
        errorDescription = "Could not connect to the AI backend. Please ensure the server is running at http://51.21.162.46:8000.";
        console.error("Failed to fetch error - backend server might not be running");
      } else if (String(error).includes("405")) {
        errorDescription = "CORS issue detected (405 Method Not Allowed). Add CORS middleware to your backend.";
        console.error("CORS issue detected");
      } else if (error.name === "AbortError") {
        errorDescription = "Request timed out. The backend server took too long to respond.";
        console.error("Request timeout");
      } else {
        console.error("Other error:", String(error));
      }

      toast({
        title: "Connection Error",
        description: errorDescription,
        variant: "destructive",
      });

      return getRandomMockResponse();
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (message.trim()) {
      const userMessage: Message = { text: message, isUser: true };
      setMessages((prev) => [...prev, userMessage]);
      setCurrentMessage("");

      const response = await processMessageWithBackend(message);
      
      if (response) {
        const aiMessage: Message = { 
          text: response.output, 
          isUser: false,
          agent_name: response.agent_name,
          agent_type: response.agent_type,
          voice_text: response.voice_text || response.output, // Use voice_text if available, otherwise fallback to output
          display_images: response.display_images // Add display_images to the message
        };
        console.log("Creating AI message:", {
          agent_name: response.agent_name,
          agent_type: response.agent_type,
          voice_text: response.voice_text
        });
        setMessages((prev) => [...prev, aiMessage]);
        // Trigger a refresh of calendar and logs sections after successful message processing
        setRefreshTrigger(prev => prev + 1);
      }
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Server debug removed */}
      <header className="w-full bg-card border-b border-border py-4">
        <div className="relative w-full px-5">
          <div className="flex items-center justify-center">
            <div className="flex flex-col items-center relative">
              <span className="font-medium text-3xl tracking-tight">ORBYTT</span>
              <div className="text-xs text-muted-foreground tracking-widest uppercase mt-0.5">Let the Orbits Align</div>
            </div>
          </div>
          
          <div className="absolute right-5 top-1/2 transform -translate-y-1/2">
            <Avatar className="h-10 w-10 border border-border">
              <AvatarImage src="https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=256&q=80" alt="Profile" />
              <AvatarFallback>OR</AvatarFallback>
            </Avatar>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-3 py-5 max-w-full flex-grow">
        <div className="grid grid-cols-12 gap-5">
          <div className={`${leftCollapsed ? 'col-span-1' : 'col-span-3 lg:col-span-2'} relative transition-all duration-300`}>
            <Button 
              variant="outline" 
              size="sm" 
              className="absolute -right-3 top-1/2 z-10 h-8 w-8 rounded-full p-0 bg-card border border-border"
              onClick={() => setLeftCollapsed(!leftCollapsed)}
            >
              {leftCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
            </Button>
            
            {leftCollapsed ? (
              <div className="h-full bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-2 flex items-center justify-center shadow-lg">
                <CalendarIcon className="h-5 w-5 text-blue-500 dark:text-blue-400" />
              </div>
            ) : (
              <div className="space-y-4 h-[calc(100vh-7.5rem)] overflow-auto">
                <CalendarSection refreshTrigger={refreshTrigger} />
                <LogsSection refreshTrigger={refreshTrigger} />
              </div>
            )}
          </div>

          <div className={`${leftCollapsed && rightCollapsed ? 'col-span-10' : leftCollapsed || rightCollapsed ? 'col-span-8 lg:col-span-9' : 'col-span-6 lg:col-span-8'} flex flex-col h-[calc(100vh-7.5rem)]`}>
            <div className="flex-grow rounded-md bg-card border border-border overflow-hidden flex flex-col">
              <MessageArea messages={messages} isLoading={isLoading} />
              <MessageInput 
                currentMessage={currentMessage}
                setCurrentMessage={setCurrentMessage}
                handleSendMessage={handleSendMessage}
                isLoading={isLoading}
              />
            </div>
          </div>

          <div className={`${rightCollapsed ? 'col-span-1' : 'col-span-3 lg:col-span-2'} relative transition-all duration-300`}>
            <Button 
              variant="outline" 
              size="sm" 
              className="absolute -left-3 top-1/2 z-10 h-8 w-8 rounded-full p-0 bg-card border border-border"
              onClick={() => setRightCollapsed(!rightCollapsed)}
            >
              {rightCollapsed ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </Button>
            
            {rightCollapsed ? (
              <div className="h-full bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-2 flex items-center justify-center shadow-lg">
                <Youtube className="h-5 w-5 text-red-600" />
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 h-[calc(100vh-7.5rem)] overflow-hidden shadow-lg p-3">
                <YoutubeSection />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const CalendarIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
    <line x1="16" x2="16" y1="2" y2="6" />
    <line x1="8" x2="8" y1="2" y2="6" />
    <line x1="3" x2="21" y1="10" y2="10" />
  </svg>
);

export default Index;
