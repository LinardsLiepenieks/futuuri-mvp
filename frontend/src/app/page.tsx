'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';

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
    const envBase = process.env.NEXT_PUBLIC_API_URL;
  const fallback = process.env.NEXT_PUBLIC_API_FALLBACK || 'http://localhost:8000';
  const candidates = [envBase, fallback];

    let finished = false;

    const tryFetch = async () => {
      for (const base of candidates) {
        if (!base) continue;
        try {
          const res = await fetch(`${base.replace(/\/$/, '')}/api/reports`, {
            cache: 'no-store',
          });
          if (!res.ok) continue;
          const data = await res.json();
          setReports(data.items || []);
          finished = true;
          break;
        } catch (err) {
          // try next candidate
        }
      }

      if (!finished) {
        // Last attempt: try relative path (same-origin)
        try {
          const res = await fetch(`/api/reports`, { cache: 'no-store' });
          if (res.ok) {
            const data = await res.json();
            setReports(data.items || []);
          } else {
            setReports([]);
          }
        } catch (err) {
          setReports([]);
        }
      }

      setLoading(false);
    };

    tryFetch();
  }, []);

  return (
    <div className="min-h-screen p-8 sm:p-16 bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      <main className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-semibold">Reports</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            List of processed reports
          </p>
        </header>

        {loading ? (
          <div className="text-center py-12">Loading reports…</div>
        ) : reports && reports.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {reports.map((r) => (
              <label
                key={r.report_id}
                className="flex items-center gap-3 p-4 border rounded-lg shadow-sm hover:shadow-md transition-colors cursor-pointer bg-white dark:bg-gray-800"
              >
                <input
                  type="checkbox"
                  className="w-4 h-4"
                  aria-label="select report"
                />
                <div className="flex-1 text-left">
                  <div className="font-mono text-xs text-gray-600 dark:text-gray-300 truncate">
                    {r.report_id}
                  </div>
                  <div className="mt-1 text-sm font-medium">Report</div>
                  <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    Created: {new Date(r.created_at).toLocaleString()} •
                    Updated: {new Date(r.updated_at).toLocaleString()}
                  </div>
                </div>
                <div className="ml-2">
                  <button className="px-3 py-1 rounded bg-blue-600 text-white text-sm">
                    Open
                  </button>
                </div>
              </label>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">No reports yet.</div>
        )}
      </main>
    </div>
  );
}
