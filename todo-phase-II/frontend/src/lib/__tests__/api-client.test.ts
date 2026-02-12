/**
 * Test suite for ApiClient.
 * Tests automatic JWT token injection, error handling, and HTTP methods.
 */

import { ApiClient, apiClient } from '../api-client';
import * as authConfig from '@/auth/auth-config';

// Mock auth-config module
jest.mock('@/auth/auth-config', () => ({
  getToken: jest.fn(),
  removeToken: jest.fn(),
  getAuthHeader: jest.fn(),
}));

describe('ApiClient', () => {
  let client: ApiClient;
  const mockBaseUrl = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
    (authConfig.getToken as jest.Mock).mockClear();
    (authConfig.removeToken as jest.Mock).mockClear();

    // Create a fresh client instance for each test
    client = new ApiClient({ baseUrl: mockBaseUrl });
  });

  describe('Constructor', () => {
    it('should initialize with default base URL from environment', () => {
      const defaultClient = new ApiClient();
      expect(defaultClient).toBeInstanceOf(ApiClient);
    });

    it('should initialize with custom base URL', () => {
      const customUrl = 'https://api.example.com';
      const customClient = new ApiClient({ baseUrl: customUrl });
      expect(customClient).toBeInstanceOf(ApiClient);
    });

    it('should initialize with custom headers', () => {
      const customHeaders = { 'X-Custom-Header': 'value' };
      const customClient = new ApiClient({ headers: customHeaders });
      expect(customClient).toBeInstanceOf(ApiClient);
    });
  });

  describe('GET Requests', () => {
    it('should make a GET request to the specified endpoint', async () => {
      const mockResponse = { data: 'test' };
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      const result = await client.get('/test-endpoint');

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/test-endpoint`,
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should include JWT token in Authorization header when available', async () => {
      const mockToken = 'mock-jwt-token';
      const mockResponse = { data: 'test' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(mockToken);

      await client.get('/protected-endpoint');

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/protected-endpoint`,
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );
    });
  });

  describe('POST Requests', () => {
    it('should make a POST request with data', async () => {
      const mockData = { name: 'Test', value: 123 };
      const mockResponse = { success: true };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      const result = await client.post('/create', mockData);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/create`,
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(mockData),
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should include JWT token in Authorization header', async () => {
      const mockToken = 'mock-jwt-token';
      const mockData = { name: 'Test' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(mockToken);

      await client.post('/create', mockData);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );
    });
  });

  describe('PUT Requests', () => {
    it('should make a PUT request with data', async () => {
      const mockData = { id: 1, name: 'Updated' };
      const mockResponse = { success: true };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      const result = await client.put('/update/1', mockData);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/update/1`,
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(mockData),
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('PATCH Requests', () => {
    it('should make a PATCH request with data', async () => {
      const mockData = { name: 'Patched' };
      const mockResponse = { success: true };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      const result = await client.patch('/patch/1', mockData);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/patch/1`,
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(mockData),
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('DELETE Requests', () => {
    it('should make a DELETE request', async () => {
      const mockResponse = { success: true };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      const result = await client.delete('/delete/1');

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/delete/1`,
        expect.objectContaining({
          method: 'DELETE',
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 Unauthorized by removing token and redirecting', async () => {
      const mockToken = 'expired-token';
      const originalLocation = window.location.href;

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Unauthorized' }),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(mockToken);

      // Mock window.location
      delete window.location;
      window.location = { href: '' } as any;

      await expect(client.get('/protected')).rejects.toThrow('Unauthorized');

      expect(authConfig.removeToken).toHaveBeenCalled();
      expect(window.location.href).toBe('/auth/sign-in');
    });

    it('should handle HTTP error responses', async () => {
      const errorMessage = 'Bad Request';
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: errorMessage }),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      await expect(client.get('/bad-endpoint')).rejects.toThrow(errorMessage);
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      await expect(client.get('/endpoint')).rejects.toThrow('Network error');
    });

    it('should handle error responses without message field', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      await expect(client.get('/endpoint')).rejects.toThrow('HTTP error! status: 500');
    });

    it('should handle responses that fail to parse as JSON', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      await expect(client.get('/endpoint')).rejects.toThrow('HTTP error! status: 500');
    });
  });

  describe('Token Injection', () => {
    it('should automatically inject token for all HTTP methods', async () => {
      const mockToken = 'test-token';
      const mockResponse = { success: true };

      (authConfig.getToken as jest.Mock).mockReturnValue(mockToken);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      // Test all methods
      await client.get('/test');
      await client.post('/test', {});
      await client.put('/test', {});
      await client.patch('/test', {});
      await client.delete('/test');

      // Verify token was included in all requests
      expect(global.fetch).toHaveBeenCalledTimes(5);
      const calls = (global.fetch as jest.Mock).mock.calls;

      calls.forEach((call) => {
        expect(call[1].headers.Authorization).toBe(`Bearer ${mockToken}`);
      });
    });

    it('should not include Authorization header when token is not available', async () => {
      (authConfig.getToken as jest.Mock).mockReturnValue(null);
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({}),
      });

      await client.get('/test');

      const [, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(options.headers.Authorization).toBeUndefined();
    });
  });

  describe('Helper Methods', () => {
    it('should allow setting a new base URL', () => {
      const newBaseUrl = 'https://new-api.example.com';
      client.setBaseUrl(newBaseUrl);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      client.get('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        `${newBaseUrl}/test`,
        expect.any(Object)
      );
    });

    it('should allow setting default headers', () => {
      const customHeaders = { 'X-Custom': 'value' };
      client.setDefaultHeaders(customHeaders);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      client.get('/test');

      const [, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(options.headers['X-Custom']).toBe('value');
    });

    it('should get current token', () => {
      const mockToken = 'test-token';
      (authConfig.getToken as jest.Mock).mockReturnValue(mockToken);

      const token = client.getCurrentToken();
      expect(token).toBe(mockToken);
      expect(authConfig.getToken).toHaveBeenCalled();
    });

    it('should check if user is authenticated', () => {
      (authConfig.getToken as jest.Mock).mockReturnValue('token');
      expect(client.isAuthenticated()).toBe(true);

      (authConfig.getToken as jest.Mock).mockReturnValue(null);
      expect(client.isAuthenticated()).toBe(false);
    });
  });

  describe('Singleton Instance', () => {
    it('should export a singleton instance', () => {
      expect(apiClient).toBeInstanceOf(ApiClient);
    });
  });

  describe('Custom Headers in Request Options', () => {
    it('should merge custom headers with default headers', async () => {
      const customHeader = { 'X-Request-ID': '12345' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });
      (authConfig.getToken as jest.Mock).mockReturnValue(null);

      await client.get('/test', { headers: customHeader });

      const [, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(options.headers['X-Request-ID']).toBe('12345');
      expect(options.headers['Content-Type']).toBe('application/json');
    });
  });
});
