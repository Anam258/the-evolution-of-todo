import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { storeToken } from '@/auth/auth-config';

interface SignInFormData {
  email: string;
  password: string;
}

interface SignInFormProps {
  onSignIn?: (userData: { token: string; userId: number; email: string }) => void;
  onError?: (error: string) => void;
  redirectAfterSignIn?: string;
}

const SignInForm: React.FC<SignInFormProps> = ({
  onSignIn,
  onError,
  redirectAfterSignIn = '/dashboard'
}) => {
  const router = useRouter();
  const [formData, setFormData] = useState<SignInFormData>({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (error) setError(null);
    if (onError) onError(null as any);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true);
    setError(null);
    if (onError) onError(null as any);

    try {
      // Call backend API for login
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const responseData = await response.json();

      if (!response.ok) {
        const errorMessage = responseData.error?.message || 'Login failed';
        throw new Error(errorMessage);
      }

      // Extract token from response
      const token = responseData.data?.token;
      const userId = responseData.data?.user_id;
      const email = responseData.data?.email;

      if (!token) {
        throw new Error('No token received from server');
      }

      // Store the token
      storeToken(token);

      // Call the onSignIn callback if provided
      if (onSignIn) {
        onSignIn({ token, userId, email });
        return; // Prevent default redirect when callback is provided
      }

      // Default behavior: redirect to dashboard
      router.push(redirectAfterSignIn);
      router.refresh(); // Refresh the router to update auth state
    } catch (err: any) {
      console.error('Sign in error:', err);
      const errorMsg = err.message || 'An error occurred during login';
      setError(errorMsg);
      if (onError) onError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      {error && (
        <div className="rounded-md bg-red-50 p-4 mb-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">{error}</h3>
            </div>
          </div>
        </div>
      )}

      <form className="space-y-6" onSubmit={handleSubmit}>
        <input type="hidden" name="remember" defaultValue="true" />

        <div className="rounded-md shadow-sm -space-y-px">
          <div>
            <label htmlFor="email-address" className="sr-only">
              Email address
            </label>
            <input
              id="email-address"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Email address"
            />
          </div>

          <div>
            <label htmlFor="password" className="sr-only">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleChange}
              className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="text-sm">
            <Link href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
              Forgot your password?
            </Link>
          </div>
        </div>

        <div>
          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? 'Signing In...' : 'Sign in'}
          </button>
        </div>
      </form>

      <div className="mt-4 text-center">
        <p className="text-sm text-gray-600">
          Don't have an account?{' '}
          <Link href="/auth/sign-up" className="font-medium text-indigo-600 hover:text-indigo-500">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};

export default SignInForm;