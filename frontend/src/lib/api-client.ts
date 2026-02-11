/**
 * API Client — enforces the /api/v1/{user_id}/tasks contract.
 * Every task request includes user_id in the URL AND the JWT in the header.
 */

import { getToken, removeToken } from '@/auth/auth-config';
import { parseJWT } from '@/lib/token-utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getUserId(): number | null {
  const token = getToken();
  if (!token) return null;
  const payload = parseJWT(token);
  return payload?.user_id ?? (payload?.sub ? Number(payload.sub) : null);
}

async function request<T = unknown>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;

  const opts: RequestInit = { method, headers };
  if (body && ['POST', 'PUT', 'PATCH'].includes(method)) {
    opts.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, opts);

  if (res.status === 401) {
    removeToken();
    if (typeof window !== 'undefined') window.location.href = '/auth/sign-in';
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Task-specific helpers using /api/v1/{user_id}/tasks contract ────────

export interface Task {
  id: number;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: number;
}

export interface TaskCreatePayload {
  title: string;
  description?: string | null;
  is_completed?: boolean;
}

function requireUserId(): number {
  const uid = getUserId();
  if (uid === null) {
    if (typeof window !== 'undefined') window.location.href = '/auth/sign-in';
    throw new Error('Not authenticated');
  }
  return uid;
}

export const taskApi = {
  list(): Promise<Task[]> {
    const uid = requireUserId();
    return request('GET', `/api/v1/${uid}/tasks`);
  },

  create(data: TaskCreatePayload): Promise<Task> {
    const uid = requireUserId();
    return request('POST', `/api/v1/${uid}/tasks`, {
      title: data.title,
      description: data.description ?? null,
      is_completed: data.is_completed ?? false,
    });
  },

  update(taskId: number, data: Partial<TaskCreatePayload>): Promise<Task> {
    const uid = requireUserId();
    return request('PUT', `/api/v1/${uid}/tasks/${taskId}`, data);
  },

  toggleComplete(taskId: number, is_completed: boolean): Promise<Task> {
    const uid = requireUserId();
    return request('PATCH', `/api/v1/${uid}/tasks/${taskId}`, { is_completed });
  },

  delete(taskId: number): Promise<{ message: string }> {
    const uid = requireUserId();
    return request('DELETE', `/api/v1/${uid}/tasks/${taskId}`);
  },
};

// Auth helpers (no user_id in URL)
export const authApi = {
  register(email: string, password: string) {
    return request<{ data: { user_id: number; email: string; token: string } }>(
      'POST', '/api/v1/auth/register', { email, password },
    );
  },
  login(email: string, password: string) {
    return request<{ data: { user_id: number; email: string; token: string } }>(
      'POST', '/api/v1/auth/login', { email, password },
    );
  },
  me() {
    return request<{ data: { user_id: number; email: string } }>('GET', '/api/v1/auth/me');
  },
};

export { getUserId };
