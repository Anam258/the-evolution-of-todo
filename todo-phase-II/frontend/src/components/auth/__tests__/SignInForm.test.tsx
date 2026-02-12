/**
 * Test suite for SignInForm component.
 * Tests form validation, submission, error handling, and user interactions.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignInForm from '../SignInForm';
import { storeToken } from '@/auth/auth-config';

// Mock Next.js router
const mockPush = jest.fn();
const mockRefresh = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    refresh: mockRefresh,
  }),
}));

// Mock auth-config
jest.mock('@/auth/auth-config', () => ({
  storeToken: jest.fn(),
}));

describe('SignInForm', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
    mockPush.mockClear();
    mockRefresh.mockClear();
  });

  describe('Rendering', () => {
    it('should render the sign-in form with all fields', () => {
      render(<SignInForm />);

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    it('should render the link to sign-up page', () => {
      render(<SignInForm />);

      const signUpLink = screen.getByText(/sign up/i);
      expect(signUpLink).toBeInTheDocument();
      expect(signUpLink.closest('a')).toHaveAttribute('href', '/auth/sign-up');
    });

    it('should render the forgot password link', () => {
      render(<SignInForm />);

      const forgotPasswordLink = screen.getByText(/forgot your password/i);
      expect(forgotPasswordLink).toBeInTheDocument();
    });
  });

  describe('Form Validation', () => {
    it('should require email field', async () => {
      render(<SignInForm />);

      const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
      expect(emailInput).toBeRequired();
    });

    it('should require password field', async () => {
      render(<SignInForm />);

      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
      expect(passwordInput).toBeRequired();
    });

    it('should accept valid email format', async () => {
      const user = userEvent.setup();
      render(<SignInForm />);

      const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
      await user.type(emailInput, 'test@example.com');

      expect(emailInput.value).toBe('test@example.com');
    });
  });

  describe('Form Submission', () => {
    it('should submit form with valid credentials', async () => {
      const user = userEvent.setup();
      const mockResponse = {
        success: true,
        data: {
          token: 'mock-jwt-token',
          user_id: 1,
          email: 'test@example.com',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<SignInForm />);

      // Fill in the form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');

      // Submit the form
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      // Wait for the form to be submitted
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/auth/login'),
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: 'test@example.com',
              password: 'password123',
            }),
          })
        );
      });

      // Verify token was stored
      expect(storeToken).toHaveBeenCalledWith('mock-jwt-token');

      // Verify redirect
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
      expect(mockRefresh).toHaveBeenCalled();
    });

    it('should disable submit button while loading', async () => {
      const user = userEvent.setup();

      // Mock a delayed response
      (global.fetch as jest.Mock).mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  json: async () => ({
                    data: { token: 'mock-token', user_id: 1, email: 'test@example.com' },
                  }),
                }),
              100
            )
          )
      );

      render(<SignInForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      await user.click(submitButton);

      // Button should be disabled during loading
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent(/signing in/i);

      // Wait for the async operation to complete to avoid affecting next test
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });

    it('should call onSignIn callback when provided', async () => {
      const user = userEvent.setup();
      const onSignIn = jest.fn();
      const mockResponse = {
        success: true,
        data: {
          token: 'mock-jwt-token',
          user_id: 1,
          email: 'test@example.com',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      render(<SignInForm onSignIn={onSignIn} />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(onSignIn).toHaveBeenCalledWith({
          token: 'mock-jwt-token',
          userId: 1,
          email: 'test@example.com',
        });
      });

      // Give a bit more time for any potential async operations to complete
      await new Promise(resolve => setTimeout(resolve, 100));

      // Should not redirect when callback is provided
      expect(mockPush).not.toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should display error message on failed login', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Invalid credentials';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: errorMessage },
        }),
      });

      render(<SignInForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should call onError callback when provided', async () => {
      const user = userEvent.setup();
      const onError = jest.fn();
      const errorMessage = 'Invalid credentials';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: errorMessage },
        }),
      });

      render(<SignInForm onError={onError} />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(errorMessage);
      });
    });

    it('should clear error message when user starts typing', async () => {
      const user = userEvent.setup();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: 'Invalid credentials' },
        }),
      });

      render(<SignInForm />);

      // Trigger an error
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });

      // Start typing again
      await user.type(screen.getByLabelText(/email address/i), 'x');

      // Error should be cleared
      expect(screen.queryByText(/invalid credentials/i)).not.toBeInTheDocument();
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();

      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<SignInForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('should handle missing token in response', async () => {
      const user = userEvent.setup();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { user_id: 1, email: 'test@example.com' }, // No token
        }),
      });

      render(<SignInForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText(/no token received/i)).toBeInTheDocument();
      });
    });
  });

  describe('Custom Redirect', () => {
    it('should redirect to custom path after successful login', async () => {
      const user = userEvent.setup();
      const customRedirect = '/custom-path';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { token: 'mock-token', user_id: 1, email: 'test@example.com' },
        }),
      });

      render(<SignInForm redirectAfterSignIn={customRedirect} />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith(customRedirect);
      });
    });
  });
});
