'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

type Report = {
  report_id: string;
  report_image_path: string | null;
  mask_image_path: string | null;
  created_at: string;
  updated_at: string;
};

export default function Home() {
  const [reports, setReports] = useState<Report[] | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const envBase = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');

    const tryFetch = async () => {
      if (!envBase) {
        setReports([]);
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${envBase}/api/reports`, {
          cache: 'no-store',
        });
        if (res.ok) {
          const data = await res.json();
          setReports(data.items || []);
        } else {
          setReports([]);
        }
      } catch (err) {
        setReports([]);
      }

      setLoading(false);
    };

    tryFetch();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center mb-8 space-x-3">
          <h1 className="text-3xl font-bold text-slate-800">Medical Reports</h1>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-8 text-center">
            <div className="flex items-center justify-center">
              <svg
                className="animate-spin h-8 w-8 text-blue-600"
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
              <span className="ml-3 text-slate-600">Loading reports…</span>
            </div>
          </div>
        ) : reports && reports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {reports.map((r) => (
              <div
                key={r.report_id}
                className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 hover:shadow-md transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
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
                      <h3 className="text-sm font-semibold text-slate-800">
                        Medical Report
                      </h3>
                    </div>
                    <div className="font-mono text-xs text-slate-500 truncate bg-slate-50 px-2 py-1 rounded">
                      {r.report_id}
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-xs text-slate-600">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-4 h-4 mr-2 text-slate-400"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-slate-500">Created:</span>
                    <span className="ml-1 font-medium">
                      {new Date(r.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="flex items-center text-xs text-slate-600">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      className="w-4 h-4 mr-2 text-slate-400"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
                      />
                    </svg>
                    <span className="text-slate-500">Updated:</span>
                    <span className="ml-1 font-medium">
                      {new Date(r.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <Link
                  href={`/report/${r.report_id}`}
                  className="w-full inline-block text-center bg-blue-600 text-white px-4 py-2 rounded-lg font-medium text-sm transition-all hover:bg-blue-700 hover:shadow-md"
                >
                  View Report
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-12 text-center">
            <div className="mx-auto h-16 w-16 text-slate-300 mb-4">
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
                  d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-800 mb-2">
              No reports yet
            </h3>
            <p className="text-sm text-slate-500">
              Upload your first medical image to generate a report
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
