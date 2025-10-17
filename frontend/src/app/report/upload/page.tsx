'use client';

import { useState } from 'react';
import useImageUpload from '@/hooks/useImageUpload';
import UploadForm from './components/UploadForm';
import StatusTimeline from './components/StatusTimelines';

export default function UploadPage() {
  // Custom hooks - extract all relevant state from the hook
  const { uploadImage, status, progress, serverMessage, error, data } =
    useImageUpload();

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center mb-8 space-x-3">
          <h1 className="text-3xl font-bold text-slate-800">
            Medical Image Analysis
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left column: Upload form */}
          <div className="order-2 lg:order-1">
            <UploadForm 
              uploadImage={uploadImage}
              status={status}
              data={data}
              error={error}
            />
          </div>

          {/* Right column: Status Timeline */}
          <div className="order-1 lg:order-2">
            <StatusTimeline
              serverMessage={serverMessage}
              status={status}
              progress={progress}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
