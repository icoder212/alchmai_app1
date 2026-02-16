import { useEffect, useState } from 'react';
import { connectWebSocket, disconnectWebSocket } from '@/lib/websocket';
import { TradingSignal } from '@/lib/api';

export function useSignalUpdates() {
  const [latestSignal, setLatestSignal] = useState<TradingSignal | null>(null);

  useEffect(() => {
    const socket = connectWebSocket();
    
    socket.on('new_signal', (data: { type: string; data: TradingSignal }) => {
      console.log('Received new signal via WebSocket:', data);
      setLatestSignal(data.data);
    });

    return () => {
      disconnectWebSocket();
    };
  }, []);

  return { latestSignal };
}
