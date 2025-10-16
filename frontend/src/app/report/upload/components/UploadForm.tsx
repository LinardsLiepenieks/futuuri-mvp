'use client';

import { useState } from 'react';
import SuccessMessage from './SuccessMessage';
import { UploadStatus } from '@/types/imageUpload';

type UploadFormProps = {
  uploadImage: (file: File) => Promise<any>;
};

const UploadForm: React.FC<UploadFormProps> = ({ uploadImage }) => {
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [data, setData] = useState<any | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Reset any previous errors
    setError(null);

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/gif'];
    if (!validTypes.includes(selectedFile.type)) {
      setError('Please select a valid image file (JPG, PNG, GIF)');
      return;
    }

    // Validate file size (10MB max)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit');
      return;
    }

    setFile(selectedFile);

    // Create preview
    const previewUrl = URL.createObjectURL(selectedFile);
    setPreview(previewUrl);
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    try {
      setStatus('uploading');
      const result = await uploadImage(file);

      // Only set success status if the server explicitly indicates success
      console.log('RESULT', result.status);
      if (result && result.status === 'processed') {
        setData(result);
        setStatus('success');
      } else {
        // If we get a response but it's not a success, keep the status as uploading
        console.log(
          'Upload in progress, waiting for processing to complete:',
          result
        );
      }
    } catch (err) {
      console.error('Upload failed:', err);
      setError(
        err instanceof Error ? err.message : 'Upload failed. Please try again.'
      );
      setStatus('error');
    }
  };

  // Reset the form
  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setStatus('idle');
    setData(null);
    setError(null);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <h2 className="text-xl font-bold mb-5 text-slate-800">
        Upload Medical Image
      </h2>

      {status === 'success' && data ? (
        <>
          <SuccessMessage data={data} />
          <button
            onClick={handleReset}
            className="mt-4 w-full bg-slate-100 text-slate-700 px-4 py-3 rounded-lg font-medium text-sm transition-all hover:bg-slate-200"
          >
            Upload Another Image
          </button>
        </>
      ) : (
        <form onSubmit={handleSubmit} className="mb-6">
          <div className="mb-5">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 ${
                preview
                  ? 'bg-blue-50 border-blue-300'
                  : error
                  ? 'bg-red-50 border-red-300'
                  : 'bg-slate-50 border-slate-200 hover:border-blue-400 hover:bg-blue-50'
              }`}
            >
              <input
                type="file"
                id="image"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                disabled={status === 'uploading'}
              />
              <label htmlFor="image" className="cursor-pointer">
                {!preview ? (
                  <div className="space-y-3">
                    <div className="mx-auto h-16 w-16 text-blue-600">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="w-16 h-16"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
                        />
                      </svg>
                    </div>
                    <div className="text-sm text-slate-600">
                      <span className="font-semibold text-blue-600 text-lg">
                        Click to upload
                      </span>{' '}
                      <span className="text-slate-500">or drag and drop</span>
                    </div>
                    <p className="text-xs text-slate-500">
                      PNG, JPG, GIF (max. 10MB)
                    </p>
                  </div>
                ) : (
                  <div className="relative">
                    <div className="bg-white rounded-lg p-2 shadow-md mb-4 inline-block">
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-h-56 mx-auto object-contain rounded"
                      />
                    </div>
                    <div className="flex items-center justify-center">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.5}
                        stroke="currentColor"
                        className="w-5 h-5 text-blue-600"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                        />
                      </svg>
                      <p className="ml-2 text-sm text-slate-700 font-medium">
                        {file?.name}
                      </p>
                      <p className="ml-2 text-xs text-slate-500">
                        ({(file?.size ? file.size / 1024 : 0).toFixed(1)} KB)
                      </p>
                    </div>
                    <button
                      type="button"
                      className="mt-3 text-xs text-blue-600 hover:text-blue-800 font-medium"
                      onClick={(e) => {
                        e.preventDefault();
                        setFile(null);
                        setPreview(null);
                      }}
                    >
                      Change file
                    </button>
                  </div>
                )}
              </label>
            </div>

            {error && (
              <div className="mt-2 text-red-600 text-sm flex items-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 mr-1"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                {error}
              </div>
            )}
          </div>

          <button
            type="submit"
            className={`w-full bg-blue-600 text-white px-4 py-3 rounded-lg font-medium text-sm transition-all duration-300
              ${
                !file || status === 'uploading'
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-blue-700 hover:shadow-md'
              }`}
            disabled={!file || status === 'uploading'}
          >
            {status === 'uploading' ? (
              <div className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Uploading...
              </div>
            ) : (
              'Generate Medical Report'
            )}
          </button>
        </form>
      )}
    </div>
  );
};

export default UploadForm;
