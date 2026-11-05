import { useState, type ReactNode } from 'react';
import { downloadUsageReport, sendUsageReport } from './slack';

export default function UsageReportActions({ base, demo, children }: { base: string; demo: boolean; children: ReactNode }) {
  const [busy, setBusy] = useState('');
  const [feedback, setFeedback] = useState('');
  const [failed, setFailed] = useState(false);
  async function report(share: boolean) {
    if (busy || demo) return;
    setBusy(share ? 'share' : 'download'); setFeedback(''); setFailed(false);
    try {
      if (share) {
        await sendUsageReport(base);
        setFeedback('Model usage HTML report uploaded and shared to Slack.');
      } else {
        const blob = await downloadUsageReport(base);
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url; link.download = 'erasight-model-usage.html'; link.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        setFeedback('Model usage HTML download prepared.');
      }
    } catch (error) {
      setFailed(true); setFeedback(error instanceof Error ? error.message : 'Model usage report could not be confirmed.');
    } finally { setBusy(''); }
  }
  return <><div className="title-actions" style={{ flexWrap: 'wrap' }}>
    {children}
    <button disabled={!!busy || demo} onClick={() => report(false)}>{busy === 'download' ? 'Preparing report...' : 'Model Usage Report'}</button>
    <button disabled={!!busy || demo} onClick={() => report(true)}>{busy === 'share' ? 'Sharing report...' : 'Send usage report to Slack'}</button>
  </div><p className="muted" role={failed ? 'alert' : 'status'}>{feedback || (demo ? 'Usage reporting requires the live backend.' : 'Download recorded model accounting; advisory runs are separate from the deterministic pipeline.')}</p></>;
}
