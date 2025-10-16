// types/status.ts

// Server response data structure
export interface ResponseData {
  id: string;
  url: string;
  filename: string;
  size: number;
  uploadedAt: string;
  status: 'processed' | 'processing' | 'error';
}

// WebSocket message types from server
export type ServerMessageType = 'status' | 'progress' | 'success' | 'error';

// Base message interface
interface BaseServerMessage {
  type: ServerMessageType;
  message?: string; // Optional human-readable message
}

// Status message from server
export interface ServerStatusMessage extends BaseServerMessage {
  type: 'status';
  message: string; // Human-readable status update
}

// Progress message from server
export interface ServerProgressMessage extends BaseServerMessage {
  type: 'progress';
  progress: number;
  received: number;
  total: number;
  message?: string;
}

// Success message from server
export interface ServerSuccessMessage extends BaseServerMessage {
  type: 'success';
  data: ResponseData;
  message?: string;
}

// Error message from server
export interface ServerErrorMessage extends BaseServerMessage {
  type: 'error';
  error: string;
  message?: string;
}

// Union type for all server message types
export type ServerMessage =
  | ServerStatusMessage
  | ServerProgressMessage
  | ServerSuccessMessage
  | ServerErrorMessage;

// Status message for the UI timeline
export interface StatusMessage {
  id: string;
  text: string;
  type: 'info' | 'processing' | 'success' | 'error' | 'websocket';
  timestamp: Date;
  details?: string;
}
