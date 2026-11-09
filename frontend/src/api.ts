import { useEffect, useState } from 'react';

export type Remote<T> = { status: 'loading' } | { status: 'error'; code?: number } | { status: 'ok'; data: T };

export function useApi<T>(url: string) {
  const [state, setState] = useState<Remote<T>>({ status: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading' });
    fetch(url, { signal: controller.signal })
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then((data: T) => setState({ status: 'ok', data }))
      .catch(code => { if (!controller.signal.aborted) setState({ status: 'error', code: typeof code === 'number' ? code : undefined }); });
    return () => controller.abort();
  }, [url, attempt]);
  return [state, () => setAttempt(n => n + 1)] as const;
}
