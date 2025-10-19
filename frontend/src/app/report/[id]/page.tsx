'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

type Report = {
  report_id: string;
  report_image_path?: string | null;
  mask_image_path?: string | null;
  report_image_url?: string | null;
  mask_image_url?: string | null;
  created_at: string;
  updated_at: string;
};

function buildFallbackUrls(report: Report) {
  // Only use the single configured API host from env (NEXT_PUBLIC_API_URL).
  const base = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '');
  if (!base) return { reportUrl: null, maskUrl: null };

  const filename = report.report_image_path
    ? report.report_image_path.split('/').pop()
    : null;

  const reportUrl = filename
    ? `${base}/api/files/${report.report_id}/report/${filename}`
    : null;
  const maskUrl = `${base}/api/files/${report.report_id}/mask`;

  return { reportUrl, maskUrl };
}

function ImageWithStatus({
  src,
  alt,
  className,
}: {
  src?: string | null;
  alt: string;
  className?: string;
}) {
  const [state, setState] = useState<'idle' | 'loading' | 'loaded' | 'error'>(
    'idle'
  );

  if (!src) {
    return <div className="text-sm text-slate-500">No image available</div>;
  }

  return (
    <div className="relative">
      {state !== 'loaded' && (
        <div className="absolute inset-0 flex items-center justify-center">
          {state === 'loading' ? (
            <div className="text-slate-400">Loading image…</div>
          ) : null}
          {state === 'error' ? (
            <div className="text-sm text-red-500">Failed to load image</div>
          ) : null}
        </div>
      )}
      <img
        src={src}
        alt={alt}
        className={`${className ?? ''} ${
          state !== 'loaded' ? 'opacity-0' : 'opacity-100'
        } transition-opacity duration-200`}
        loading="lazy"
        onLoad={() => setState('loaded')}
        onError={() => setState('error')}
        onLoadStart={() => setState('loading')}
      />
    </div>
  );
}

export default function ReportPage({ params }: { params: any }) {
  // `params` may be a Promise in newer Next.js versions. Unwrap it with React.use()
  const { id } = (React.use(params) as { id: string }) || {};
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let mounted = true;

    const fetchReports = async () => {
      try {
        // Fetch reports only from the single env-configured API host.
        const envBase = (process.env.NEXT_PUBLIC_API_URL || '').replace(
          /\/$/,
          ''
        );
        let found: Report | null = null;

        if (!envBase) {
          // No API configured — cannot fetch reports from browser
          if (mounted) {
            setLoading(false);
            setReport(null);
          }
          return;
        }

        try {
          const res = await fetch(`${envBase}/api/reports`, {
            cache: 'no-store',
          });
          if (res.ok) {
            const data = await res.json();
            const items: Report[] = data.items || [];
            const match = items.find((it) => it.report_id === id);
            if (match) found = match;
          }
        } catch (e) {
          // network error — treat as not found
        }

        if (!found && mounted) {
          setLoading(false);
          setReport(null);
          return;
        }

        if (mounted) {
          // If report doesn't include image URLs, build fallback ones
          const urls = buildFallbackUrls(found as Report);
          const copy: Report = { ...(found as Report) };
          copy.report_image_url = copy.report_image_url || urls.reportUrl;
          copy.mask_image_url = copy.mask_image_url || urls.maskUrl;
          setReport(copy);
          setLoading(false);
        }
      } catch (err) {
        if (mounted) {
          setReport(null);
          setLoading(false);
        }
      }
    };

    fetchReports();

    return () => {
      mounted = false;
    };
  }, [id, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-8 text-center">
            Loading report…
          </div>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-8 text-center">
            <h3 className="text-lg font-semibold text-slate-800">
              Report not found
            </h3>
            <p className="text-sm text-slate-500">
              The requested report was not found.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <div className="mb-4 flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-slate-800">
                Report {report.report_id}
              </h1>
              <div className="text-sm text-slate-500 mt-1">
                Created: {new Date(report.created_at).toLocaleString()}
                {' • '}
                Updated: {new Date(report.updated_at).toLocaleString()}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            {report.report_image_url ? (
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">
                  Report image
                </h3>
                <img
                  src={report.report_image_url as string}
                  alt="Report image"
                  className="w-full rounded-lg shadow-sm object-contain"
                  loading="lazy"
                />
              </div>
            ) : (
              <div className="text-sm text-slate-500">
                No report image available
              </div>
            )}

            {report.mask_image_url ? (
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">
                  Mask image
                </h3>
                <img
                  src={report.mask_image_url as string}
                  alt="Mask image"
                  className="w-full rounded-lg shadow-sm object-contain"
                  loading="lazy"
                />
              </div>
            ) : (
              <div className="text-sm text-slate-500">
                No mask image available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
