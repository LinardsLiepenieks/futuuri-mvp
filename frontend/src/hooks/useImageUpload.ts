// hooks/useImageUpload.ts
import { useState, useRef, useEffect } from 'react';

// Define the possible upload statuses
export type UploadStatus =
  | 'idle'
  | 'connecting'
  | 'uploading'
  | 'processing'
  | 'success'
  | 'error';

// Define the type for response data
interface ResponseData {
  id: string;
  filename: string;
  size: number;
  uploadedAt: string;
  status: string;
  url?: string;
}

/**
 * Prepares the image data for WebSocket upload
 * @param file The file to prepare for upload
 * @returns An object containing the file data and metadata
 */
const prepareWebSocketData = async (file: File) => {
  console.log('Preparing image for WebSocket upload:', file.name);

  // Convert file to ArrayBuffer for WebSocket transfer
  const arrayBuffer = await file.arrayBuffer();

  // Create the metadata object that will be sent first
  const metadata = {
    type: 'metadata',
    filename: file.name,
    size: file.size,
    contentType: file.type,
    lastModified: file.lastModified,
  };

  return {
    metadata: metadata,
    binaryData: arrayBuffer,
  };
};

export function useImageUpload() {
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [data, setData] = useState<ResponseData | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [error, setError] = useState<Error | null>(null);
  const [serverMessage, setServerMessage] = useState<string | null>(null);

  // WebSocket reference
  const websocketRef = useRef<WebSocket | null>(null);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      if (
        websocketRef.current &&
        websocketRef.current.readyState === WebSocket.OPEN
      ) {
        websocketRef.current.close();
        console.log('WebSocket connection closed on cleanup');
      }
    };
  }, []);

  /**
   * Connect to the WebSocket server
   * @returns A promise that resolves when the connection is established
   */
  const connectWebSocket = (): Promise<WebSocket> => {
    return new Promise((resolve, reject) => {
      setStatus('connecting');
      console.log('Attempting to connect to WebSocket server...');

      // Build WebSocket URL from configured API host. If API uses https, use wss.
      const api = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
      const wsUrl = api
        ? api.replace(/^http/, 'ws') + '/api/upload/ws'
        : 'ws://localhost:8000/api/upload/ws';
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connection established');
        websocketRef.current = ws;
        setServerMessage('WebSocket connection established');
        resolve(ws);
      };

      ws.onerror = (error) => {
        console.error('WebSocket connection error:', error);
        setStatus('error');
        setError(new Error('Failed to establish WebSocket connection'));
        setServerMessage('Connection error');
        reject(new Error('Failed to establish WebSocket connection'));
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('Received message from server:', message);

          // Handle different message types from server
          switch (message.type) {
            case 'status':
              setServerMessage(message.message);
              break;

            case 'progress':
              setProgress(message.progress);
              setServerMessage(message.message);
              break;

            case 'success':
              setStatus('success');
              setData(message.data);
              setServerMessage(message.message);
              break;

            case 'error':
              setStatus('error');
              setError(new Error(message.error || 'Unknown error'));
              setServerMessage(message.message || 'Upload error');
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log(
          `WebSocket connection closed: ${event.code} ${event.reason}`
        );
        setServerMessage(
          `Connection closed: ${event.reason || 'Unknown reason'}`
        );
        websocketRef.current = null;
      };
    });
  };

  /**
   * Upload an image file to the server via WebSocket
   */
  const uploadImage = async (file: File): Promise<ResponseData> => {
    setStatus('uploading');
    setError(null);
    setProgress(0);
    setServerMessage(null);
    setData(null);

    try {
      // Prepare the data for WebSocket transmission
      const preparedData = await prepareWebSocketData(file);
      console.log('Data prepared for WebSocket upload:', {
        metadataSize: JSON.stringify(preparedData.metadata).length,
        binaryDataSize: preparedData.binaryData.byteLength,
      });

      // Connect to WebSocket server
      const ws = await connectWebSocket();

      // Create a promise that will be resolved when upload completes
      return new Promise((resolve, reject) => {
        try {
          // Send the metadata first
          console.log('Sending metadata:', preparedData.metadata);
          ws.send(JSON.stringify(preparedData.metadata));

          // Send the file data after a short delay (give server time to process metadata)
          setTimeout(() => {
            try {
              console.log('Sending file data...');
              setStatus('uploading');
              ws.send(preparedData.binaryData);
            } catch (error) {
              console.error('Error sending file data:', error);
              reject(new Error('Error sending file data'));
            }
          }, 100);

          // Create a listener to resolve the promise when upload succeeds
          const messageHandler = (event: MessageEvent) => {
            try {
              const message = JSON.parse(event.data);

              if (message.type === 'success') {
                // Remove the message handler
                ws.removeEventListener('message', messageHandler);

                // Resolve the promise with the response data
                resolve(message.data);
              } else if (message.type === 'error') {
                // Remove the message handler
                ws.removeEventListener('message', messageHandler);

                // Reject the promise with the error
                reject(new Error(message.error || 'Upload failed'));
              }
            } catch (error) {
              console.error('Error handling message in upload promise:', error);
            }
          };

          // Add the message handler
          ws.addEventListener('message', messageHandler);

          // Also handle WebSocket errors
          const errorHandler = () => {
            ws.removeEventListener('message', messageHandler);
            reject(new Error('WebSocket error during upload'));
          };

          ws.addEventListener('error', errorHandler);

          // Handle WebSocket close
          const closeHandler = () => {
            ws.removeEventListener('message', messageHandler);
            ws.removeEventListener('error', errorHandler);
          };

          ws.addEventListener('close', closeHandler);
        } catch (error) {
          console.error('Error in WebSocket send operation:', error);
          reject(error);
        }
      });
    } catch (err) {
      setStatus('error');
      const errorObject =
        err instanceof Error ? err : new Error('Failed to prepare data');
      setError(errorObject);
      throw errorObject;
    }
  };

  return {
    status,
    data,
    error,
    progress,
    serverMessage,
    uploadImage,
  };
}

export default useImageUpload;
