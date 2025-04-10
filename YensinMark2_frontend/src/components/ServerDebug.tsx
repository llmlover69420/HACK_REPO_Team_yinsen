import { useEffect, useState } from 'react';

const ServerDebug = () => {
  const [serverInfo, setServerInfo] = useState({
    mode: '',
    url: ''
  });

  useEffect(() => {
    const mode = import.meta.env.VITE_SERVER_MODE || 'main';
    const url = mode === 'test' ? 'http://localhost:8000' : 'http://51.21.162.46:8000';
    
    setServerInfo({
      mode,
      url
    });
    
    console.log('Server Debug Component:');
    console.log('- Mode:', mode);
    console.log('- URL:', url);
    console.log('- Raw env var:', import.meta.env.VITE_SERVER_MODE);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 bg-white dark:bg-gray-800 p-3 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
      <h3 className="text-sm font-bold mb-1">Server Debug Info</h3>
      <div className="text-xs space-y-1">
        <p><span className="font-medium">Mode:</span> {serverInfo.mode}</p>
        <p><span className="font-medium">URL:</span> {serverInfo.url}</p>
        <p><span className="font-medium">Raw Env:</span> {import.meta.env.VITE_SERVER_MODE || 'undefined'}</p>
      </div>
    </div>
  );
};

export default ServerDebug;
