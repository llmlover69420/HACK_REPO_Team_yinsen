
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ClipboardList, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface NotificationLog {
  timestamp: string;
  message: string;
  // Additional potential fields from backend
  text?: string;
  event?: string;
  description?: string;
  date?: string;
}

interface LogsSectionProps {
  refreshTrigger?: number;
}

const LogsSection = ({ refreshTrigger = 0 }: LogsSectionProps) => {
  const [logs, setLogs] = useState<NotificationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get server URL from environment variable
  const serverMode = import.meta.env.VITE_SERVER_MODE || 'main';
  const serverUrl = serverMode === 'test' ? 'http://localhost:8000' : 'http://51.21.162.46:8000';

  useEffect(() => {
    console.log('LogsSection: Fetching logs with refreshTrigger =', refreshTrigger);
    console.log('LogsSection: Using server URL:', serverUrl);
    
    setLoading(true);
    const fetchLogs = async () => {
      try {
        console.log('LogsSection: Fetching from', `${serverUrl}/read_notification_logs`);
        const response = await fetch(`${serverUrl}/read_notification_logs`);
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => 'No error details');
          console.error('LogsSection: Fetch failed with status', response.status, errorText);
          throw new Error(`Failed to fetch notification logs: ${response.status} ${errorText}`);
        }
        
        const data = await response.json();
        console.log('LogsSection: Received data', data);
        
        // Check different potential formats
        if (Array.isArray(data)) {
          console.log('LogsSection: Data is an array with length', data.length);
          // Limit to the most recent 5 entries
          setLogs(data.slice(-5));
        } else if (data.logs && Array.isArray(data.logs)) {
          console.log('LogsSection: Data has logs array with length', data.logs.length);
          
          // Parse the logs format which might be HTML strings
          const parsedLogs = data.logs.map((item, index) => {
            if (typeof item === 'string') {
              return {
                id: index,
                message: item,
                timestamp: new Date().toISOString()
              };
            }
            return item;
          });
          
          // Limit to the most recent 5 entries
          const limitedLogs = parsedLogs.slice(-5);
          setLogs(limitedLogs);
        } else {
          console.log('LogsSection: Unexpected data format', typeof data, data);
          setLogs([]);
        }
      } catch (err) {
        console.error('LogsSection: Error fetching logs', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch notification logs');
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [refreshTrigger, serverUrl]); // Re-fetch when refreshTrigger or serverUrl changes

  return (
    <Card className="w-full shadow-md border-0 bg-gradient-to-b from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
      <CardHeader className="pb-2">
        <CardTitle className="text-md font-medium flex items-center gap-2 text-purple-800 dark:text-purple-300">
          <div className="bg-purple-100 dark:bg-purple-900 p-1.5 rounded-full">
            <ClipboardList className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          </div>
          Logs
        </CardTitle>
      </CardHeader>
      <CardContent className="pb-3">
        <div className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-purple-600 dark:text-purple-400" />
            </div>
          ) : error ? (
            <div className="text-xs text-red-500 dark:text-red-400 p-2">{error}</div>
          ) : logs.length === 0 ? (
            <div className="text-xs text-gray-500 dark:text-gray-400 p-2">No notification logs found</div>
          ) : (
            logs.map((log, index) => (
              <div 
                key={index}
                className="flex gap-3 items-start p-2 rounded-md hover:bg-purple-100/50 dark:hover:bg-purple-900/30 transition-colors"
              >
                <div className="text-purple-500 dark:text-purple-400">•</div>
                <div className="text-xs text-gray-700 dark:text-gray-300" 
                  dangerouslySetInnerHTML={{ __html: log.message || log.text || log.event || '' }}
                />
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default LogsSection;
