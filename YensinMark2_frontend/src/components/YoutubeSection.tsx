
import { Card, CardContent } from "@/components/ui/card";
import { Youtube, Play, X } from "lucide-react";
import { AspectRatio } from "@/components/ui/aspect-ratio";
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface YoutubeItem {
  id: number;
  title: string;
  channel: string;
  thumbnail: string;
  url: string;
}

const YoutubeSection = () => {
  const [activeVideoId, setActiveVideoId] = useState<number | null>(null);
  
  // YouTube items with matching content and URLs
  const youtubeItems: YoutubeItem[] = [
    {
      id: 1,
      title: "How to Build a React App in 10 Minutes",
      channel: "CodeMaster",
      thumbnail: "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=Tn6-PIqc4UM"
    },
    {
      id: 2,
      title: "Learn Tailwind CSS - Complete Course",
      channel: "CSS Wizards",
      thumbnail: "https://images.unsplash.com/photo-1487058792275-0ad4aaf24ca7?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=lCxcTsOHrjo"
    },
    {
      id: 3,
      title: "TypeScript Tips and Tricks",
      channel: "TS Guru",
      thumbnail: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=30LWjhZzg50"
    },
    {
      id: 4,
      title: "Building Modern UIs - Design Patterns",
      channel: "UI Masters",
      thumbnail: "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=MqYm3LIcpoQ"
    },
    {
      id: 5,
      title: "Next.js 13 Crash Course - Server Components",
      channel: "Web Dev Simplified",
      thumbnail: "https://images.unsplash.com/photo-1533073526757-2c8ca1df9f1c?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=Y6KDk5iyrYE"
    },
    {
      id: 6,
      title: "Mastering CSS Grid Layout",
      channel: "Frontend Masters",
      thumbnail: "https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=EiNiSFIPIQE"
    },
    {
      id: 7,
      title: "React Query: Complete Tutorial",
      channel: "React Experts",
      thumbnail: "https://images.unsplash.com/photo-1550063873-ab792950096b?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=novnyCaa7To"
    },
    {
      id: 8,
      title: "Building a Full Stack App with Prisma",
      channel: "Database Pros",
      thumbnail: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=RebA5J-rlwg"
    },
    {
      id: 9,
      title: "Advanced TypeScript Patterns",
      channel: "TypeScript Wizards",
      thumbnail: "https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=F7O4gA0RRKc"
    },
    {
      id: 10,
      title: "Micro-Animations for Better UX",
      channel: "UX Design Lab",
      thumbnail: "https://images.unsplash.com/photo-1542831371-29b0f74f9713?auto=format&fit=crop&w=320&h=180",
      url: "https://www.youtube.com/watch?v=yGbZ6ikwYhU"
    }
  ];

  return (
    <div className="space-y-3">
      <Card className="p-3 bg-card border border-border">
        <h2 className="text-md font-medium flex items-center gap-2">
          <Youtube className="h-5 w-5 text-destructive" />
          <span>Videos</span>
        </h2>
      </Card>
      
      <div className="grid gap-3 max-h-[calc(100vh-8rem)] overflow-y-auto pr-1 scrollbar scrollbar-thin scrollbar-thumb-muted-foreground/40 scrollbar-track-transparent">
        {youtubeItems.map((item) => (
          <div 
            key={item.id}
            className="block group transition-transform duration-300 transform hover:-translate-y-1 cursor-pointer"
            onClick={() => {
              // Toggle video playback
              setActiveVideoId(activeVideoId === item.id ? null : item.id);
            }}
          >
            <Card className="overflow-hidden border border-border hover:border-primary/30 transition-all duration-300">
              {activeVideoId === item.id ? (
                <div className="relative">
                  <AspectRatio ratio={16/9}>
                    <iframe
                      width="100%"
                      height="100%"
                      src={`https://www.youtube.com/embed/${new URL(item.url).searchParams.get('v') || item.url.split('/').pop()}?autoplay=1`}
                      title="YouTube video player"
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    ></iframe>
                  </AspectRatio>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="absolute top-1 right-1 h-6 w-6 bg-background/70 hover:bg-background/90 text-foreground rounded-full p-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      setActiveVideoId(null);
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div className="relative">
                  <AspectRatio ratio={16/9}>
                    <img 
                      src={item.thumbnail} 
                      alt={item.title} 
                      className="w-full h-full object-cover"
                    />
                  </AspectRatio>
                  <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                    <div className="bg-background/90 rounded-full p-2 transform scale-90 group-hover:scale-100 transition-transform duration-300">
                      <Play className="h-4 w-4 text-destructive" />
                    </div>
                  </div>
                </div>
              )}
              
              <CardContent className="py-2 px-3 bg-card">
                <h3 className="font-medium text-xs line-clamp-1 mb-1">{item.title}</h3>
                <p className="text-muted-foreground text-xs">{item.channel}</p>
              </CardContent>
            </Card>
          </div>
        ))}
      </div>

    </div>
  );
};

export default YoutubeSection;
