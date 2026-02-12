/**
 * Test suite for SignUpForm component.
 * Tests form validation, submission, error handling, and user interactions.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignUpForm from '../SignUpForm';
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

describe('SignUpForm', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
    mockPush.mockClear();
    mockRefresh.mockClear();
  });

  describe('Rendering', () => {
    it('should render the sign-up form with all fields', () => {
      render(<SignUpForm />);

      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
    });

    it('should render the link to sign-in page', () => {
      render(<SignUpForm />);

      const signInLink = screen.getByText(/sign in/i);
      expect(signInLink).toBeInTheDocument();
      expect(signInLink.closest('a')).toHaveAttribute('href', '/auth/sign-in');
    });
  });

  describe('Form Validation', () => {
    it('should require all fields', () => {
      render(<SignUpForm />);

      const emailInput = screen.getByLabelText(/email address/i) as HTMLInputElement;
      const passwordInput = screen.getByLabelText(/^password$/i) as HTMLInputElement;
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;

      expect(emailInput).toBeRequired();
      expect(passwordInput).toBeRequired();
      expect(confirmPasswordInput).toBeRequired();
    });

    it('should validate password length (minimum 8 characters)', async () => {
      const user = userEvent.setup();
      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'short');
      await user.type(screen.getByLabelText(/confirm password/i), 'short');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      });

      // Verify that fetch was not called
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should validate password confirmation matches', async () => {
      const user = userEvent.setup();
      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'differentpassword');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });

      // Verify that fetch was not called
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should accept valid email format', async () => {
      const user = userEvent.setup();
      render(<SignUpForm />);

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

      render(<SignUpForm />);

      // Fill in the form
      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');

      // Submit the form
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      // Wait for the form to be submitted
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/auth/register'),
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

      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');

      const submitButton = screen.getByRole('button', { name: /sign up/i });
      await user.click(submitButton);

      // Button should be disabled during loading
      expect(submitButton).toBeDisabled();
      expect(submitButton).toHaveTextContent(/creating account/i);

      // Wait for the async operation to complete to avoid affecting next test
      await waitFor(() => {
        expect(submitButton).not.toBeDisabled();
      });
    });

    it('should call onSignUp callback when provided', async () => {
      const user = userEvent.setup();
      const onSignUp = jest.fn();
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

      render(<SignUpForm onSignUp={onSignUp} />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(onSignUp).toHaveBeenCalledWith({
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
    it('should display error message on failed registration', async () => {
      const user = userEvent.setup();
      const errorMessage = 'Email already exists';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: errorMessage },
        }),
      });

      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should call onError callback when provided', async () => {
      const user = userEvent.setup();
      const onError = jest.fn();
      const errorMessage = 'Email already exists';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: errorMessage },
        }),
      });

      render(<SignUpForm onError={onError} />);

      await user.type(screen.getByLabelText(/email address/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(onError).toHaveBeenCalledWith(errorMessage);
      });
    });

    it('should clear error message when user starts typing', async () => {
      const user = userEvent.setup();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          error: { message: 'Email already exists' },
        }),
      });

      render(<SignUpForm />);

      // Trigger an error
      await user.type(screen.getByLabelText(/email address/i), 'existing@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
      });

      // Start typing again
      await user.type(screen.getByLabelText(/email address/i), 'x');

      // Error should be cleared
      expect(screen.queryByText(/email already exists/i)).not.toBeInTheDocument();
    });

    it('should handle network errors', async () => {
      const user = userEvent.setup();

      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

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

      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(screen.getByText(/no token received/i)).toBeInTheDocument();
      });
    });
  });

  describe('Client-side Validation', () => {
    it('should show password mismatch error before making API call', async () => {
      const user = userEvent.setup();
      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'different123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      // Error should be shown immediately without making API call
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      expect(global.fetch).not.toHaveBeenCalled();
    });

    it('should show password length error before making API call', async () => {
      const user = userEvent.setup();
      render(<SignUpForm />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'short');
      await user.type(screen.getByLabelText(/confirm password/i), 'short');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      // Error should be shown immediately without making API call
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });

  describe('Custom Redirect', () => {
    it('should redirect to custom path after successful registration', async () => {
      const user = userEvent.setup();
      const customRedirect = '/welcome';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: { token: 'mock-token', user_id: 1, email: 'test@example.com' },
        }),
      });

      render(<SignUpForm redirectAfterSignUp={customRedirect} />);

      await user.type(screen.getByLabelText(/email address/i), 'test@example.com');
      await user.type(screen.getByLabelText(/^password$/i), 'password123');
      await user.type(screen.getByLabelText(/confirm password/i), 'password123');
      await user.click(screen.getByRole('button', { name: /sign up/i }));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith(customRedirect);
      });
    });
  });
});
