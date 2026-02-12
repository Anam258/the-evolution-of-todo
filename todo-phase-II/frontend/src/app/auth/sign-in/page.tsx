'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { storeToken } from '@/auth/auth-config';
import { authApi } from '@/lib/api-client';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await authApi.login(email, password);
      storeToken(res.data.token);
      router.push('/');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center">
      <div className="fixed inset-0 -z-10 gradient-mesh opacity-30" />
      <div className="fixed inset-0 -z-10 bg-background/80" />

      <div className="w-full max-w-sm px-4">
        <div className="glass-card-elevated p-8 space-y-6">
          <div className="text-center">
            <h1 className="text-xl font-semibold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              TaskPulse AI
            </h1>
            <p className="text-sm text-muted-foreground mt-1">Sign in to continue</p>
          </div>

          {error && (
            <div className="glass-card border-destructive/30 bg-destructive/5 p-3 text-sm text-destructive text-center">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground font-medium">Email</label>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="glass-input h-10"
                required
                autoFocus
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-muted-foreground font-medium">Password</label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 chars, 1 upper, 1 digit"
                className="glass-input h-10"
                required
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              className="w-full h-10 bg-primary/90 hover:bg-primary text-primary-foreground glow-primary transition-all"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>

          <p className="text-center text-xs text-muted-foreground">
            No account?{' '}
            <Link href="/auth/sign-up" className="text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
