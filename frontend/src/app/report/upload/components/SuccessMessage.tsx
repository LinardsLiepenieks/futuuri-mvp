'use client';

import { FC } from 'react';

type SuccessMessageProps = {
  data: {
    id: string;
    filename: string;
    size: number;
    uploadedAt: string | number | Date;
    status: string;
  };
};

const SuccessMessage: FC<SuccessMessageProps> = ({ data }) => {
  return (
    <div className="mt-6 rounded-lg overflow-hidden border border-zinc-100 shadow-sm">
      <div className="bg-emerald-50 py-3 px-4 border-b border-emerald-100">
        <h2 className="text-md font-semibold text-emerald-800 flex items-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 mr-2"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          Medical Image Uploaded Successfully
        </h2>
      </div>
      <div className="p-4 bg-white">
        <div className="space-y-2 text-sm">
          <div className="flex">
            <span className="text-zinc-500 w-24">ID:</span>
            <span className="font-mono text-zinc-700">{data.id}</span>
          </div>
          <div className="flex">
            <span className="text-zinc-500 w-24">Filename:</span>
            <span className="text-zinc-700">{data.filename}</span>
          </div>
          <div className="flex">
            <span className="text-zinc-500 w-24">Size:</span>
            <span className="text-zinc-700">
              {(data.size / 1024).toFixed(2)} KB
            </span>
          </div>
          <div className="flex">
            <span className="text-zinc-500 w-24">Uploaded:</span>
            <span className="text-zinc-700">
              {new Date(data.uploadedAt).toLocaleString()}
            </span>
          </div>
          <div className="flex items-center">
            <span className="text-zinc-500 w-24">Status:</span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
              {data.status}
            </span>
          </div>
        </div>
        <div className="mt-4 pt-3 border-t border-zinc-100">
          <button className="text-sm font-medium text-emerald-600 hover:text-emerald-800 transition-colors flex items-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            Download Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuccessMessage;
