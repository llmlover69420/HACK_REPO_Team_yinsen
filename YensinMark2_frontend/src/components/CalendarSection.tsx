
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar as CalendarIcon, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface CalendarLog {
  date: string;
  time: string;
  event: string;
  // Additional potential fields from backend
  activity?: string;
  message?: string;
  description?: string;
}

interface CalendarSectionProps {
  refreshTrigger?: number;
}

const CalendarSection = ({ refreshTrigger = 0 }: CalendarSectionProps) => {
  const [calendarLogs, setCalendarLogs] = useState<CalendarLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get server URL from environment variable
  const serverMode = import.meta.env.VITE_SERVER_MODE || 'main';
  const serverUrl = serverMode === 'test' ? 'http://localhost:8000' : 'http://51.21.162.46:8000';

  useEffect(() => {
    console.log('CalendarSection: Fetching logs with refreshTrigger =', refreshTrigger);
    console.log('CalendarSection: Using server URL:', serverUrl);
    
    setLoading(true);
    const fetchCalendarLogs = async () => {
      try {
        console.log('CalendarSection: Fetching from', `${serverUrl}/read_calender_logs`);
        const response = await fetch(`${serverUrl}/read_calender_logs`);
        
        if (!response.ok) {
          const errorText = await response.text().catch(() => 'No error details');
          console.error('CalendarSection: Fetch failed with status', response.status, errorText);
          throw new Error(`Failed to fetch calendar logs: ${response.status} ${errorText}`);
        }
        
        const data = await response.json();
        console.log('CalendarSection: Received data', data);
        
        // Check different potential formats
        if (Array.isArray(data)) {
          console.log('CalendarSection: Data is an array with length', data.length);
          setCalendarLogs(data);
        } else if (data.logs && Array.isArray(data.logs)) {
          console.log('CalendarSection: Data has logs array with length', data.logs.length);
          
          // Parse the logs format: "09:00 AM | Breakfast"
          const parsedLogs = data.logs.map((item, index) => {
            if (typeof item === 'string') {
              const parts = item.split('|');
              return {
                id: index,
                time: parts[0]?.trim() || '',
                event: parts[1]?.trim() || ''
              };
            }
            return item;
          });
          
          setCalendarLogs(parsedLogs);
        } else {
          console.log('CalendarSection: Unexpected data format', typeof data, data);
          setCalendarLogs([]);
        }
      } catch (err) {
        console.error('CalendarSection: Error fetching logs', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch calendar logs');
      } finally {
        setLoading(false);
      }
    };

    fetchCalendarLogs();
  }, [refreshTrigger, serverUrl]); // Re-fetch when refreshTrigger or serverUrl changes

  return (
    <Card className="w-full shadow-md border-0 bg-gradient-to-b from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950">
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-md font-medium flex items-center gap-2 text-blue-800 dark:text-blue-300">
          <div className="bg-blue-100 dark:bg-blue-900 p-1.5 rounded-full">
            <CalendarIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          </div>
          Today's Schedule
        </CardTitle>
      </CardHeader>
      
      <CardContent className="pb-4">
        <div className="space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600 dark:text-blue-400" />
            </div>
          ) : error ? (
            <div className="text-xs text-red-500 dark:text-red-400 p-2">{error}</div>
          ) : calendarLogs.length === 0 ? (
            <div className="text-xs text-gray-500 dark:text-gray-400 p-2">No calendar events found</div>
          ) : (
            calendarLogs.map((item, index) => (
              <div 
                key={index}
                className="flex gap-3 items-start p-2 rounded-md hover:bg-blue-100/50 dark:hover:bg-blue-900/30 transition-colors"
              >
                <div className="min-w-[80px] text-xs font-medium text-blue-700 dark:text-blue-400">{item.time}</div>
                <div className="text-xs text-gray-700 dark:text-gray-300">{item.event || item.activity || item.message}</div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default CalendarSection;
