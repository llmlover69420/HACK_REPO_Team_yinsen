import React, { useState, useEffect, useRef } from 'react';
import { X, Minimize, Maximize, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';

interface YoutubePiPProps {
  videoId: string | null;
  onClose: () => void;
}

const YoutubePiP: React.FC<YoutubePiPProps> = ({ videoId, onClose }) => {
  const [minimized, setMinimized] = useState(false);
  const [position, setPosition] = useState({ x: 20, y: window.innerHeight - 220 });
  const [dragging, setDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle dragging functionality
  useEffect(() => {
    if (!containerRef.current) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (dragging) {
        const newX = e.clientX - dragOffset.x;
        const newY = e.clientY - dragOffset.y;
        
        // Ensure the component stays within viewport bounds
        const maxX = window.innerWidth - (containerRef.current?.offsetWidth || 0);
        const maxY = window.innerHeight - (containerRef.current?.offsetHeight || 0);
        
        setPosition({
          x: Math.max(0, Math.min(newX, maxX)),
          y: Math.max(0, Math.min(newY, maxY))
        });
      }
    };

    const handleMouseUp = () => {
      setDragging(false);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [dragging, dragOffset]);

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (containerRef.current) {
      setDragging(true);
      setDragOffset({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      });
    }
  };

  // Extract video ID from URL if a full URL is provided
  const getVideoId = (idOrUrl: string): string => {
    if (idOrUrl.includes('youtube.com') || idOrUrl.includes('youtu.be')) {
      const url = new URL(idOrUrl);
      if (idOrUrl.includes('youtube.com')) {
        return url.searchParams.get('v') || '';
      } else {
        return url.pathname.slice(1);
      }
    }
    return idOrUrl;
  };

  const extractedVideoId = videoId ? getVideoId(videoId) : '';

  // Open video in new tab
  const openInNewTab = () => {
    if (extractedVideoId) {
      window.open(`https://www.youtube.com/watch?v=${extractedVideoId}`, '_blank');
    }
  };

  if (!videoId) return null;

  return (
    <div
      ref={containerRef}
      className={`fixed z-50 transition-all duration-300 shadow-xl rounded-lg overflow-hidden ${
        minimized ? 'w-64 h-12' : 'w-80 md:w-96'
      }`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
      }}
    >
      {/* Header/Drag handle */}
      <div
        className="bg-black text-white p-2 flex items-center justify-between cursor-move"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-red-500"></div>
          <span className="text-xs truncate">YouTube Player</span>
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-white hover:bg-white/20"
            onClick={() => setMinimized(!minimized)}
          >
            {minimized ? <Maximize className="h-3 w-3" /> : <Minimize className="h-3 w-3" />}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-white hover:bg-white/20"
            onClick={openInNewTab}
          >
            <ExternalLink className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-white hover:bg-white/20"
            onClick={onClose}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Video content */}
      {!minimized && (
        <div className="bg-black">
          <iframe
            width="100%"
            height="215"
            src={`https://www.youtube.com/embed/${extractedVideoId}?autoplay=1`}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
      )}
    </div>
  );
};

export default YoutubePiP;
