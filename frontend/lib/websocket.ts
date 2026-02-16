// Native WebSocket implementation (compatible with FastAPI WebSocket)
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

let socket: WebSocket | null = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 1000;
let eventHandlers: { [key: string]: ((data: any) => void)[] } = {};

export function connectWebSocket(): any {
  if (socket?.readyState === WebSocket.OPEN) {
    return createSocketInterface();
  }

  try {
    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      console.log("WebSocket connected");
      reconnectAttempts = 0;
      triggerEvent("connect", null);
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      triggerEvent("disconnect", null);
      
      // Auto-reconnect
      if (reconnectAttempts < maxReconnectAttempts) {
        reconnectAttempts++;
        setTimeout(() => {
          console.log(`Reconnecting... (attempt ${reconnectAttempts})`);
          connectWebSocket();
        }, reconnectDelay);
      }
    };

    socket.onerror = (error) => {
      console.error("WebSocket error:", error);
      triggerEvent("error", error);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type) {
          triggerEvent(data.type, data);
        }
      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    };
  } catch (error) {
    console.error("Error creating WebSocket:", error);
  }

  return createSocketInterface();
}

function createSocketInterface() {
  return {
    on: (event: string, handler: (data: any) => void) => {
      if (!eventHandlers[event]) {
        eventHandlers[event] = [];
      }
      eventHandlers[event].push(handler);
    },
    off: (event: string, handler?: (data: any) => void) => {
      if (!handler) {
        delete eventHandlers[event];
      } else if (eventHandlers[event]) {
        eventHandlers[event] = eventHandlers[event].filter(h => h !== handler);
      }
    },
    connected: socket?.readyState === WebSocket.OPEN,
  };
}

function triggerEvent(event: string, data: any) {
  if (eventHandlers[event]) {
    eventHandlers[event].forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in ${event} handler:`, error);
      }
    });
  }
}

export function disconnectWebSocket() {
  if (socket) {
    socket.close();
    socket = null;
    eventHandlers = {};
  }
}

export function getSocket(): WebSocket | null {
  return socket;
}
