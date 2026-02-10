'use client';

import { useState, useRef, useEffect } from 'react';
import { Task, taskApi } from '@/lib/api-client';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'system';
  text: string;
  timestamp: Date;
}

interface Props {
  tasks: Task[];
  onMutate: () => void;
}

const HELP_TEXT = `Commands:
  add <title>           — create a task
  add <title> | <desc>  — create with description
  done <id>             — mark complete
  undo <id>             — mark incomplete
  delete <id>           — remove a task
  edit <id> <new title> — rename a task
  list                  — show all tasks
  pending               — show pending only
  completed             — show completed only
  clear                 — clear chat history
  help                  — show this message`;

export default function ChatInterface({ tasks, onMutate }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    { id: '0', role: 'system', text: 'Welcome to Nuralyx Flow. Type `help` for commands.', timestamp: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [processing, setProcessing] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function push(role: 'user' | 'system', text: string) {
    setMessages((prev) => [...prev, { id: crypto.randomUUID(), role, text, timestamp: new Date() }]);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const raw = input.trim();
    if (!raw) return;
    setInput('');
    push('user', raw);
    setProcessing(true);

    try {
      const result = await processCommand(raw, tasks);
      if (result.mutated) onMutate();
      push('system', result.reply);
    } catch (err: unknown) {
      push('system', `Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setProcessing(false);
    }
  }

  function handleClear() {
    setMessages([{ id: crypto.randomUUID(), role: 'system', text: 'Chat cleared. Type `help` for commands.', timestamp: new Date() }]);
  }

  return (
    <div className="glass-card-elevated flex flex-col h-[calc(100vh-16rem)] min-h-[400px]">
      {/* Messages */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-3">
          {messages.map((msg) => (
            <div key={msg.id} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              <div className={cn(
                'max-w-[85%] rounded-2xl px-4 py-2.5 text-sm whitespace-pre-wrap',
                msg.role === 'user'
                  ? 'bg-primary/20 text-foreground rounded-br-md'
                  : 'bg-white/[0.04] text-foreground/90 rounded-bl-md border border-white/[0.04]',
              )}>
                <span className="font-mono text-[13px] leading-relaxed">{msg.text}</span>
              </div>
            </div>
          ))}
          <div ref={endRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-white/[0.06] flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={processing ? 'Processing...' : 'Type a command...'}
          disabled={processing}
          className="glass-input flex-1 h-10 text-sm font-mono"
          autoFocus
        />
        <Button
          type="submit"
          disabled={processing || !input.trim()}
          size="sm"
          className="h-10 px-4 bg-primary/80 hover:bg-primary text-primary-foreground"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={handleClear} className="h-10 px-3 text-muted-foreground hover:text-foreground" title="Clear chat">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
        </Button>
      </form>
    </div>
  );
}

/* ── Command processor ────────────────────────────────────────────────── */

async function processCommand(
  raw: string,
  tasks: Task[],
): Promise<{ reply: string; mutated: boolean }> {
  const lower = raw.toLowerCase().trim();

  if (lower === 'help') return { reply: HELP_TEXT, mutated: false };

  if (lower === 'list') {
    if (tasks.length === 0) return { reply: 'No tasks found.', mutated: false };
    const lines = tasks.map((t) =>
      `[${t.is_completed ? 'x' : ' '}] #${t.id} ${t.title}`
    );
    return { reply: lines.join('\n'), mutated: false };
  }

  if (lower === 'pending') {
    const p = tasks.filter((t) => !t.is_completed);
    if (p.length === 0) return { reply: 'No pending tasks.', mutated: false };
    return { reply: p.map((t) => `[ ] #${t.id} ${t.title}`).join('\n'), mutated: false };
  }

  if (lower === 'completed') {
    const c = tasks.filter((t) => t.is_completed);
    if (c.length === 0) return { reply: 'No completed tasks.', mutated: false };
    return { reply: c.map((t) => `[x] #${t.id} ${t.title}`).join('\n'), mutated: false };
  }

  if (lower === 'clear') return { reply: 'Use the clear button.', mutated: false };

  // add <title> | <description>
  if (lower.startsWith('add ')) {
    const rest = raw.slice(4).trim();
    const parts = rest.split('|').map((s) => s.trim());
    const title = parts[0];
    const description = parts[1] || null;
    if (!title) return { reply: 'Usage: add <title> [| <description>]', mutated: false };
    const task = await taskApi.create({ title, description });
    return { reply: `Created task #${task.id}: ${task.title}`, mutated: true };
  }

  // done <id>
  if (lower.startsWith('done ')) {
    const id = parseInt(raw.slice(5).trim().replace('#', ''));
    if (isNaN(id)) return { reply: 'Usage: done <id>', mutated: false };
    await taskApi.toggleComplete(id, true);
    return { reply: `Task #${id} marked as complete.`, mutated: true };
  }

  // undo <id>
  if (lower.startsWith('undo ')) {
    const id = parseInt(raw.slice(5).trim().replace('#', ''));
    if (isNaN(id)) return { reply: 'Usage: undo <id>', mutated: false };
    await taskApi.toggleComplete(id, false);
    return { reply: `Task #${id} marked as incomplete.`, mutated: true };
  }

  // delete <id>
  if (lower.startsWith('delete ')) {
    const id = parseInt(raw.slice(7).trim().replace('#', ''));
    if (isNaN(id)) return { reply: 'Usage: delete <id>', mutated: false };
    await taskApi.delete(id);
    return { reply: `Task #${id} deleted.`, mutated: true };
  }

  // edit <id> <new title>
  if (lower.startsWith('edit ')) {
    const rest = raw.slice(5).trim();
    const spaceIdx = rest.indexOf(' ');
    if (spaceIdx === -1) return { reply: 'Usage: edit <id> <new title>', mutated: false };
    const id = parseInt(rest.slice(0, spaceIdx).replace('#', ''));
    const newTitle = rest.slice(spaceIdx + 1).trim();
    if (isNaN(id) || !newTitle) return { reply: 'Usage: edit <id> <new title>', mutated: false };
    await taskApi.update(id, { title: newTitle });
    return { reply: `Task #${id} updated to: ${newTitle}`, mutated: true };
  }

  return { reply: `Unknown command: "${raw}". Type \`help\` for available commands.`, mutated: false };
}
