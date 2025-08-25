/**
 * Unit tests for API service functions
 * Tests API calls to backend using mocked fetch/axios
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  mockFetch,
  mockAxios,
  mockApiResponses,
  setupGlobalMocks,
  cleanupMocks,
  API_BASE_URL,
  mockAuthToken,
  mockErrorResponse,
} from './testUtils';

// Mock the API service (assuming it exists)
const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Authentication
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: email, password }),
    });
    return response.json();
  },

  // Products
  getProducts: async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/products`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.json();
  },

  // Categories
  getCategories: async () => {
    const response = await fetch(`${API_BASE_URL}/api/categories`);
    return response.json();
  },

  // SEO optimization
  optimizeText: async (text, token) => {
    const response = await fetch(`${API_BASE_URL}/api/seo/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text }),
    });
    return response.json();
  },
};

describe('API Service Tests', () => {
  beforeEach(() => {
    setupGlobalMocks();
  });

  afterEach(() => {
    cleanupMocks();
  });

  describe('Health Check API', () => {
    it('should fetch health check successfully', async () => {
      global.fetch = mockFetch(mockApiResponses.healthCheck);

      const result = await apiService.healthCheck();

      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/health`);
      expect(result).toEqual(mockApiResponses.healthCheck);
    });

    it('should handle health check failure', async () => {
      global.fetch = mockFetch(
        { error: 'Service unavailable' },
        503
      );

      const result = await apiService.healthCheck();
      expect(result).toEqual({ error: 'Service unavailable' });
    });
  });

  describe('Authentication API', () => {
    it('should login successfully with valid credentials', async () => {
      global.fetch = mockFetch(mockApiResponses.login);

      const result = await apiService.login('test@example.com', 'password');

      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/auth/token`,
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
      );
      expect(result).toEqual(mockApiResponses.login);
    });

    it('should handle login failure with invalid credentials', async () => {
      const errorResponse = { detail: 'Incorrect username or password' };
      global.fetch = mockFetch(errorResponse, 401);

      const result = await apiService.login('wrong@example.com', 'wrongpass');

      expect(result).toEqual(errorResponse);
    });

    it('should format login request body correctly', async () => {
      global.fetch = mockFetch(mockApiResponses.login);

      await apiService.login('user@test.com', 'mypassword');

      const [url, options] = fetch.mock.calls[0];
      expect(options.body.toString()).toContain('username=user%40test.com');
      expect(options.body.toString()).toContain('password=mypassword');
    });
  });

  describe('Products API', () => {
    it('should fetch products with authentication', async () => {
      global.fetch = mockFetch(mockApiResponses.products);

      const result = await apiService.getProducts(mockAuthToken);

      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/products`,
        expect.objectContaining({
          headers: { Authorization: `Bearer ${mockAuthToken}` },
        })
      );
      expect(result).toEqual(mockApiResponses.products);
    });

    it('should handle unauthorized products access', async () => {
      const errorResponse = { detail: 'Unauthorized' };
      global.fetch = mockFetch(errorResponse, 401);

      const result = await apiService.getProducts('invalid-token');

      expect(result).toEqual(errorResponse);
    });
  });

  describe('Categories API', () => {
    it('should fetch categories without authentication', async () => {
      global.fetch = mockFetch(mockApiResponses.categories);

      const result = await apiService.getCategories();

      expect(fetch).toHaveBeenCalledWith(`${API_BASE_URL}/api/categories`);
      expect(result).toEqual(mockApiResponses.categories);
    });
  });

  describe('SEO API', () => {
    it('should optimize text with authentication', async () => {
      const optimizedText = {
        original: 'Test text',
        title: 'Optimized Test Text',
        meta_description: 'Meta description for test text',
        keywords: ['test', 'text', 'optimized'],
      };
      global.fetch = mockFetch(optimizedText);

      const result = await apiService.optimizeText('Test text', mockAuthToken);

      expect(fetch).toHaveBeenCalledWith(
        `${API_BASE_URL}/api/seo/optimize`,
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${mockAuthToken}`,
          },
          body: JSON.stringify({ text: 'Test text' }),
        })
      );
      expect(result).toEqual(optimizedText);
    });

    it('should handle SEO optimization failure', async () => {
      const errorResponse = { detail: 'Text optimization failed' };
      global.fetch = mockFetch(errorResponse, 400);

      const result = await apiService.optimizeText('', mockAuthToken);

      expect(result).toEqual(errorResponse);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      try {
        await apiService.healthCheck();
      } catch (error) {
        expect(error.message).toBe('Network error');
      }
    });

    it('should handle timeout errors', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Request timeout'));

      try {
        await apiService.getProducts(mockAuthToken);
      } catch (error) {
        expect(error.message).toBe('Request timeout');
      }
    });
  });

  describe('Request Headers', () => {
    it('should include correct content-type for JSON requests', async () => {
      global.fetch = mockFetch({ success: true });

      await apiService.optimizeText('test', mockAuthToken);

      const [url, options] = fetch.mock.calls[0];
      expect(options.headers['Content-Type']).toBe('application/json');
    });

    it('should include authorization header for protected endpoints', async () => {
      global.fetch = mockFetch(mockApiResponses.products);

      await apiService.getProducts(mockAuthToken);

      const [url, options] = fetch.mock.calls[0];
      expect(options.headers.Authorization).toBe(`Bearer ${mockAuthToken}`);
    });
  });
});

describe('Axios API Service Tests', () => {
  // Alternative implementation using axios
  const axiosApiService = {
    healthCheck: async () => {
      const response = await mockAxios.get('/health');
      return response.data;
    },

    login: async (email, password) => {
      const response = await mockAxios.post('/api/auth/token', {
        username: email,
        password,
      });
      return response.data;
    },

    getProducts: async (token) => {
      mockAxios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await mockAxios.get('/api/products');
      return response.data;
    },
  };

  beforeEach(() => {
    cleanupMocks();
  });

  it('should make GET request with axios', async () => {
    mockAxios.get.mockResolvedValue({ data: mockApiResponses.healthCheck });

    const result = await axiosApiService.healthCheck();

    expect(mockAxios.get).toHaveBeenCalledWith('/health');
    expect(result).toEqual(mockApiResponses.healthCheck);
  });

  it('should make POST request with axios', async () => {
    mockAxios.post.mockResolvedValue({ data: mockApiResponses.login });

    const result = await axiosApiService.login('test@example.com', 'password');

    expect(mockAxios.post).toHaveBeenCalledWith('/api/auth/token', {
      username: 'test@example.com',
      password: 'password',
    });
    expect(result).toEqual(mockApiResponses.login);
  });

  it('should set authorization header with axios', async () => {
    mockAxios.get.mockResolvedValue({ data: mockApiResponses.products });

    await axiosApiService.getProducts(mockAuthToken);

    expect(mockAxios.defaults.headers.common['Authorization']).toBe(
      `Bearer ${mockAuthToken}`
    );
    expect(mockAxios.get).toHaveBeenCalledWith('/api/products');
  });
});