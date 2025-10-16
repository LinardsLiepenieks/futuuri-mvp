'use client';

import { useState, useEffect } from 'react';

interface StatusItem {
  id: string;
  message: string;
  timestamp: Date;
}

interface StatusTimelineProps {
  serverMessage: string | null;
  status: string;
  progress: number;
}

const StatusTimeline: React.FC<StatusTimelineProps> = ({
  serverMessage,
  status,
  progress,
}) => {
  // Keep track of all status messages
  const [statusHistory, setStatusHistory] = useState<StatusItem[]>([]);
  const [lastMessage, setLastMessage] = useState<string | null>(null);

  // Update status history when server message changes
  useEffect(() => {
    if (serverMessage && serverMessage !== lastMessage) {
      // Add new message to history
      setStatusHistory((prevHistory) => [
        ...prevHistory,
        {
          id: Date.now().toString(),
          message: serverMessage,
          timestamp: new Date(),
        },
      ]);
      // Remember this message to avoid duplicates
      setLastMessage(serverMessage);
    }
  }, [serverMessage, lastMessage]);

  // Get a chronologically sorted version of the history (newest first)
  const sortedHistory = [...statusHistory].sort(
    (a, b) => b.timestamp.getTime() - a.timestamp.getTime()
  );

  // Show at most the 10 most recent messages to avoid clutter
  const recentMessages = sortedHistory.slice(0, 10);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <h2 className="text-xl font-bold mb-5 text-slate-800 flex items-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 mr-2 text-blue-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        Upload Status
      </h2>

      {/* Current Status */}
      <div className="mb-5 flex items-center">
        <span className="text-sm font-medium text-slate-700 w-24">Status:</span>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            status === 'success'
              ? 'bg-green-100 text-green-800'
              : status === 'error'
              ? 'bg-red-100 text-red-800'
              : status === 'uploading'
              ? 'bg-blue-100 text-blue-800'
              : status === 'connecting'
              ? 'bg-amber-100 text-amber-800'
              : status === 'processing'
              ? 'bg-purple-100 text-purple-800'
              : 'bg-slate-100 text-slate-800'
          }`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Progress Bar (only shown when uploading/processing) */}
      {(status === 'uploading' || status === 'processing') && progress > 0 && (
        <div className="mb-5">
          <div className="flex justify-between mb-1">
            <span className="text-sm font-medium text-slate-700 w-24">
              Progress:
            </span>
            <span className="text-sm text-slate-700">{progress}%</span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Latest Server Message */}
      {serverMessage && (
        <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-100">
          <span className="block text-xs font-medium text-blue-700 mb-1">
            Latest Update:
          </span>
          <span className="text-sm text-slate-700">{serverMessage}</span>
        </div>
      )}

      {/* Status History Timeline */}
      {statusHistory.length > 0 && (
        <div className="mt-5">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">
            Message History
          </h3>
          <div className="border-l-2 border-blue-200 pl-4 ml-2 space-y-4">
            {recentMessages.map((item) => (
              <div key={item.id} className="relative">
                <div className="absolute -left-6 mt-1.5 h-2.5 w-2.5 rounded-full bg-blue-500"></div>
                <div className="text-xs text-slate-400">
                  {item.timestamp.toLocaleTimeString()} (
                  {Math.round((Date.now() - item.timestamp.getTime()) / 1000)}s
                  ago)
                </div>
                <p className="text-sm text-slate-600 mt-1">{item.message}</p>
              </div>
            ))}

            {statusHistory.length > 10 && (
              <div className="text-xs text-slate-500 italic pt-1">
                + {statusHistory.length - 10} earlier messages
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusTimeline;
