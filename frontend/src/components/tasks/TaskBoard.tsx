'use client';

import { useState } from 'react';
import { Task, taskApi, TaskCreatePayload } from '@/lib/api-client';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface Props {
  tasks: Task[];
  onMutate: () => void;
}

export default function TaskBoard({ tasks, onMutate }: Props) {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [creating, setCreating] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDesc, setEditDesc] = useState('');

  const pending = tasks.filter((t) => !t.is_completed);
  const completed = tasks.filter((t) => t.is_completed);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      await taskApi.create({ title: title.trim(), description: desc.trim() || null });
      setTitle('');
      setDesc('');
      onMutate();
    } finally {
      setCreating(false);
    }
  }

  async function handleToggle(task: Task) {
    await taskApi.toggleComplete(task.id, !task.is_completed);
    onMutate();
  }

  async function handleDelete(id: number) {
    await taskApi.delete(id);
    onMutate();
  }

  async function handleUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (editId === null || !editTitle.trim()) return;
    await taskApi.update(editId, { title: editTitle.trim(), description: editDesc.trim() || null });
    setEditId(null);
    onMutate();
  }

  function startEdit(task: Task) {
    setEditId(task.id);
    setEditTitle(task.title);
    setEditDesc(task.description ?? '');
  }

  return (
    <div className="space-y-8">
      {/* ── Create ──────────────────────────────────────────────── */}
      <form onSubmit={handleCreate} className="glass-card p-5 space-y-3">
        <Input
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="glass-input h-11 px-4 text-sm"
          required
        />
        <Textarea
          placeholder="Description (optional)"
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          className="glass-input min-h-[60px] px-4 py-2.5 text-sm resize-none"
          rows={2}
        />
        <Button
          type="submit"
          disabled={creating || !title.trim()}
          className="w-full h-10 bg-primary/90 hover:bg-primary text-primary-foreground glow-primary transition-all"
        >
          {creating ? 'Adding...' : 'Add Task'}
        </Button>
      </form>

      {/* ── Stats ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Total', value: tasks.length, color: 'text-foreground' },
          { label: 'Pending', value: pending.length, color: 'text-amber-400' },
          { label: 'Done', value: completed.length, color: 'text-emerald-400' },
        ].map((s) => (
          <div key={s.label} className="glass-card p-4 text-center">
            <p className="text-xs text-muted-foreground tracking-wider uppercase">{s.label}</p>
            <p className={cn('text-2xl font-semibold mt-1 font-mono', s.color)}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* ── Pending ─────────────────────────────────────────────── */}
      {pending.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-xs font-medium tracking-widest uppercase text-muted-foreground px-1">
            Pending
          </h3>
          {pending.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              isEditing={editId === task.id}
              editTitle={editTitle}
              editDesc={editDesc}
              onEditTitle={setEditTitle}
              onEditDesc={setEditDesc}
              onToggle={() => handleToggle(task)}
              onEdit={() => startEdit(task)}
              onDelete={() => handleDelete(task.id)}
              onSave={handleUpdate}
              onCancel={() => setEditId(null)}
            />
          ))}
        </section>
      )}

      {/* ── Completed ───────────────────────────────────────────── */}
      {completed.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-xs font-medium tracking-widest uppercase text-muted-foreground px-1">
            Completed
          </h3>
          {completed.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              isEditing={editId === task.id}
              editTitle={editTitle}
              editDesc={editDesc}
              onEditTitle={setEditTitle}
              onEditDesc={setEditDesc}
              onToggle={() => handleToggle(task)}
              onEdit={() => startEdit(task)}
              onDelete={() => handleDelete(task.id)}
              onSave={handleUpdate}
              onCancel={() => setEditId(null)}
            />
          ))}
        </section>
      )}

      {tasks.length === 0 && (
        <div className="glass-card p-12 text-center">
          <p className="text-muted-foreground text-sm">No tasks yet. Create one above.</p>
        </div>
      )}
    </div>
  );
}

/* ── Single task card ──────────────────────────────────────────────────── */

interface TaskCardProps {
  task: Task;
  isEditing: boolean;
  editTitle: string;
  editDesc: string;
  onEditTitle: (v: string) => void;
  onEditDesc: (v: string) => void;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onSave: (e: React.FormEvent) => void;
  onCancel: () => void;
}

function TaskCard({
  task, isEditing, editTitle, editDesc,
  onEditTitle, onEditDesc, onToggle, onEdit, onDelete, onSave, onCancel,
}: TaskCardProps) {
  if (isEditing) {
    return (
      <form onSubmit={onSave} className="glass-card-elevated p-4 space-y-3 ring-1 ring-primary/20">
        <Input value={editTitle} onChange={(e) => onEditTitle(e.target.value)} className="glass-input h-9 text-sm" required />
        <Textarea value={editDesc} onChange={(e) => onEditDesc(e.target.value)} className="glass-input min-h-[48px] text-sm resize-none" rows={2} />
        <div className="flex gap-2 justify-end">
          <Button type="button" variant="ghost" size="sm" onClick={onCancel} className="text-muted-foreground hover:text-foreground">Cancel</Button>
          <Button type="submit" size="sm" className="bg-primary/90 hover:bg-primary text-primary-foreground">Save</Button>
        </div>
      </form>
    );
  }

  return (
    <div className={cn(
      'glass-card group flex items-start gap-3 p-4 transition-all hover:border-white/[0.12]',
      task.is_completed && 'opacity-50',
    )}>
      <Checkbox
        checked={task.is_completed}
        onCheckedChange={onToggle}
        className="mt-0.5 border-white/20 data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
      />
      <div className="flex-1 min-w-0">
        <p className={cn('text-sm font-medium leading-tight', task.is_completed && 'line-through text-muted-foreground')}>
          {task.title}
        </p>
        {task.description && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{task.description}</p>
        )}
        <p className="text-[10px] text-muted-foreground/60 mt-2 font-mono">
          {new Date(task.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
        </p>
      </div>
      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="sm" onClick={onEdit} className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
        </Button>
        <Button variant="ghost" size="sm" onClick={onDelete} className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
        </Button>
      </div>
    </div>
  );
}
