'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, removeToken, getToken } from '@/auth/auth-config';
import { taskApi, type Task, getUserId, authApi } from '@/lib/api-client';
import TaskBoard from '@/components/tasks/TaskBoard';
import ChatInterface from '@/components/chat/ChatInterface';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

type Mode = 'tasks' | 'chat';

export default function DashboardPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>('tasks');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskApi.list();
      setTasks(data);
    } catch (err: unknown) {
      if (err instanceof Error && err.message === 'Unauthorized') return;
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/sign-in');
      return;
    }
    fetchTasks();
    // Fetch user email
    authApi.me().then((res) => setEmail(res.data.email)).catch(() => {});
  }, [router, fetchTasks]);

  function handleLogout() {
    removeToken();
    router.push('/auth/sign-in');
  }

  if (!isAuthenticated()) return null;

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* ── Gradient mesh background ──────────────────────────────── */}
      <div className="fixed inset-0 -z-10 gradient-mesh opacity-40" />
      <div className="fixed inset-0 -z-10 bg-background/80" />

      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
        {/* ── Header ──────────────────────────────────────────────── */}
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent bg-[length:200%_auto] animate-[gradient_3s_linear_infinite]">
                Nuralyx Flow
              </span>
            </h1>
            {email && (
              <p className="text-xs text-muted-foreground mt-0.5 font-mono">{email}</p>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="text-muted-foreground hover:text-foreground text-xs"
          >
            Sign out
          </Button>
        </header>

        {/* ── Mode Toggle ─────────────────────────────────────────── */}
        <div className="glass-card p-1 flex mb-6">
          {([
            { key: 'tasks' as Mode, label: 'Tasks', icon: GridIcon },
            { key: 'chat' as Mode, label: 'Chat', icon: TerminalIcon },
          ]).map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setMode(key)}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-sm font-medium transition-all',
                mode === key
                  ? 'bg-white/[0.08] text-foreground shadow-sm glow-primary'
                  : 'text-muted-foreground hover:text-foreground/80',
              )}
            >
              <Icon />
              {label}
              {key === 'tasks' && (
                <Badge variant="secondary" className="ml-1 h-5 px-1.5 text-[10px] font-mono bg-white/[0.06] border-0">
                  {tasks.length}
                </Badge>
              )}
            </button>
          ))}
        </div>

        {/* ── Error ───────────────────────────────────────────────── */}
        {error && (
          <div className="glass-card border-destructive/30 bg-destructive/5 p-3 mb-6 text-sm text-destructive">
            {error}
            <Button variant="ghost" size="sm" onClick={fetchTasks} className="ml-2 h-6 text-xs underline text-destructive hover:text-destructive">
              Retry
            </Button>
          </div>
        )}

        {/* ── Loading ─────────────────────────────────────────────── */}
        {loading ? (
          <div className="glass-card p-16 flex flex-col items-center justify-center">
            <div className="h-8 w-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
            <p className="text-sm text-muted-foreground mt-4">Loading tasks...</p>
          </div>
        ) : (
          /* ── Views ─────────────────────────────────────────────── */
          mode === 'tasks' ? (
            <TaskBoard tasks={tasks} onMutate={fetchTasks} />
          ) : (
            <ChatInterface tasks={tasks} onMutate={fetchTasks} />
          )
        )}

        {/* ── Footer ──────────────────────────────────────────────── */}
        <footer className="mt-12 text-center">
          <p className="text-[10px] text-muted-foreground/40 font-mono tracking-wider">
            NURALYX FLOW &middot; PHASE II
          </p>
        </footer>
      </div>
    </div>
  );
}

/* ── Icons ────────────────────────────────────────────────────────────── */

function GridIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="7" height="7" x="3" y="3" rx="1" /><rect width="7" height="7" x="14" y="3" rx="1" />
      <rect width="7" height="7" x="14" y="14" rx="1" /><rect width="7" height="7" x="3" y="14" rx="1" />
    </svg>
  );
}

function TerminalIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="4 17 10 11 4 5" /><line x1="12" x2="20" y1="19" y2="19" />
    </svg>
  );
}
