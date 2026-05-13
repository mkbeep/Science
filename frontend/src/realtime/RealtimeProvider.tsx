import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { io, Socket } from 'socket.io-client';

const envSocket =
  typeof process.env.REACT_APP_SOCKET_URL === 'string'
    ? process.env.REACT_APP_SOCKET_URL.replace(/\/$/, '')
    : '';

function defaultSocketOrigin(): string {
  if (typeof window === 'undefined') {
    return 'http://localhost:5001';
  }
  return `${window.location.protocol}//${window.location.hostname}:5001`;
}

const SOCKET_URL = envSocket || defaultSocketOrigin();

export interface CrawlBanner {
  title: string;
  body?: string;
}

interface RealtimeValue {
  connected: boolean;
  refreshEpoch: number;
  lastBanner: CrawlBanner | null;
  dismissBanner: () => void;
  requestRefresh: () => void;
}

const RealtimeContext = createContext<RealtimeValue | null>(null);

export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [refreshEpoch, setRefreshEpoch] = useState(0);
  const [lastBanner, setLastBanner] = useState<CrawlBanner | null>(null);

  const dismissBanner = useCallback(() => setLastBanner(null), []);
  const requestRefresh = useCallback(
    () => setRefreshEpoch((e) => e + 1),
    [],
  );

  useEffect(() => {
    const socket: Socket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 24,
      reconnectionDelay: 2000,
    });

    socket.on('connect', () => setConnected(true));
    socket.on('disconnect', () => setConnected(false));
    socket.on('connect_error', () => setConnected(false));

    socket.on('crawl_update', (payload: Record<string, unknown>) => {
      const ev = String(payload.event || '');
      if (ev === 'crawl_complete') {
        const n = payload.new_jobs;
        const total = payload.jobs_crawled;
        setLastBanner({
          title: 'Đã có bản crawl mới',
          body: `${n ?? '?'} tin mới được thêm (${total ?? '?'} job đã quét).`,
        });
        setRefreshEpoch((x) => x + 1);
        try {
          if (
            typeof window !== 'undefined' &&
            typeof Notification !== 'undefined' &&
            Notification.permission === 'granted'
          ) {
            new Notification('Việc làm IT Việt Nam', {
              body: `Cập nhật dữ liệu: ${n ?? '?'} tin mới.`,
            });
          }
        } catch {
          /* ignore unsupported notifications */
        }
      } else if (ev === 'crawl_warning') {
        setLastBanner({
          title: 'Crawler cảnh báo',
          body: String(payload.message || 'Kiểm tra log crawler.'),
        });
      }
    });

    return () => {
      socket.close();
    };
  }, []);

  const value = useMemo(
    () => ({
      connected,
      refreshEpoch,
      lastBanner,
      dismissBanner,
      requestRefresh,
    }),
    [connected, refreshEpoch, lastBanner, dismissBanner, requestRefresh],
  );

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  );
}

export function useRealtime(): RealtimeValue {
  const ctx = useContext(RealtimeContext);
  if (!ctx) {
    throw new Error('useRealtime requires RealtimeProvider');
  }
  return ctx;
}
