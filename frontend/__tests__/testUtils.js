/**
 * Test utilities for components and API calls
 */
import { render } from '@testing-library/react';
import { vi } from 'vitest';

// Mock API base URL
export const API_BASE_URL = 'http://localhost:8000';

// Mock fetch function
export const mockFetch = (responseData, status = 200) => {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => responseData,
    text: async () => JSON.stringify(responseData),
  });
};

// Mock axios
export const mockAxios = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
  create: vi.fn(() => mockAxios),
  defaults: { baseURL: API_BASE_URL },
  interceptors: {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  },
};

// Mock authentication token
export const mockAuthToken = 'mock-jwt-token-123';

// Mock user data
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  isActive: true,
};

// Mock API responses
export const mockApiResponses = {
  login: {
    access_token: mockAuthToken,
    token_type: 'bearer',
    user: mockUser,
  },
  products: [
    {
      id: 'MLB123456789',
      title: 'Test Product 1',
      price: 299.99,
      currency_id: 'BRL',
      status: 'active',
    },
    {
      id: 'MLB987654321', 
      title: 'Test Product 2',
      price: 599.99,
      currency_id: 'BRL',
      status: 'active',
    },
  ],
  categories: [
    { id: 'MLB1132', name: 'Telefones e Celulares' },
    { id: 'MLB1144', name: 'Eletrodomésticos' },
  ],
  healthCheck: { status: 'ok' },
};

// Utility to render component with common providers
export const renderWithProviders = (ui, options = {}) => {
  // If you have context providers (Redux, React Router, etc.), wrap them here
  return render(ui, options);
};

// Mock localStorage
export const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

// Setup global mocks
export const setupGlobalMocks = () => {
  global.fetch = mockFetch(mockApiResponses.healthCheck);
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
  });
};

// Cleanup mocks
export const cleanupMocks = () => {
  vi.clearAllMocks();
  mockLocalStorage.getItem.mockClear();
  mockLocalStorage.setItem.mockClear();
  mockLocalStorage.removeItem.mockClear();
  mockLocalStorage.clear.mockClear();
};

// API call helpers for testing
export const makeAuthenticatedRequest = (url, options = {}) => {
  return {
    url,
    options: {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${mockAuthToken}`,
        'Content-Type': 'application/json',
      },
    },
  };
};

// Error response helpers
export const mockErrorResponse = (status, message) => ({
  ok: false,
  status,
  json: async () => ({ detail: message }),
});

export default {
  mockFetch,
  mockAxios,
  mockAuthToken,
  mockUser,
  mockApiResponses,
  renderWithProviders,
  setupGlobalMocks,
  cleanupMocks,
  makeAuthenticatedRequest,
  mockErrorResponse,
};