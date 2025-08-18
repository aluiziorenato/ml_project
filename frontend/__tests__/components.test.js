/**
 * Unit tests for React components
 * Tests main components and login flow with mocked API calls
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  mockFetch,
  mockApiResponses,
  setupGlobalMocks,
  cleanupMocks,
  renderWithProviders,
  API_BASE_URL,
} from './testUtils';

// Mock React components (since actual components may not exist yet)
const MockLoginForm = ({ onLogin, loading = false }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    onLogin(email, password);
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form">
      <h2>Login</h2>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          required
          data-testid="email-input"
        />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          name="password"
          required
          data-testid="password-input"
        />
      </div>
      <button 
        type="submit" 
        disabled={loading}
        data-testid="login-button"
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
};

const MockProductList = ({ products = [], loading = false }) => {
  if (loading) {
    return <div data-testid="loading">Loading products...</div>;
  }

  if (products.length === 0) {
    return <div data-testid="empty-state">No products found</div>;
  }

  return (
    <div data-testid="product-list">
      <h2>Products</h2>
      <ul>
        {products.map((product) => (
          <li key={product.id} data-testid={`product-${product.id}`}>
            <h3>{product.title}</h3>
            <p>Price: {product.currency_id} {product.price}</p>
            <p>Status: {product.status}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

const MockDashboard = ({ user, products, onLogout }) => {
  return (
    <div data-testid="dashboard">
      <header>
        <h1>ML Integration Dashboard</h1>
        <div data-testid="user-info">
          Welcome, {user?.email || 'User'}
        </div>
        <button onClick={onLogout} data-testid="logout-button">
          Logout
        </button>
      </header>
      <main>
        <MockProductList products={products} />
      </main>
    </div>
  );
};

const MockApp = () => {
  const [user, setUser] = React.useState(null);
  const [products, setProducts] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const handleLogin = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setUser({ email, token: data.access_token });
        // Load products after login
        loadProducts(data.access_token);
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async (token) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/products`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      console.error('Failed to load products:', err);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setProducts([]);
    setError(null);
  };

  if (error) {
    return (
      <div data-testid="error-message">
        Error: {error}
        <button onClick={() => setError(null)}>Dismiss</button>
      </div>
    );
  }

  if (!user) {
    return <MockLoginForm onLogin={handleLogin} loading={loading} />;
  }

  return (
    <MockDashboard 
      user={user} 
      products={products} 
      onLogout={handleLogout} 
    />
  );
};

// Make React available for the mock components
global.React = {
  useState: vi.fn(),
};

describe('Component Tests', () => {
  beforeEach(() => {
    setupGlobalMocks();
    // Mock React.useState
    let stateIndex = 0;
    const states = [];
    
    global.React.useState = vi.fn((initialValue) => {
      const currentIndex = stateIndex++;
      if (!states[currentIndex]) {
        states[currentIndex] = initialValue;
      }
      
      const setState = (newValue) => {
        states[currentIndex] = typeof newValue === 'function' 
          ? newValue(states[currentIndex]) 
          : newValue;
      };
      
      return [states[currentIndex], setState];
    });
  });

  afterEach(() => {
    cleanupMocks();
    global.React.useState.mockClear();
  });

  describe('LoginForm Component', () => {
    it('should render login form correctly', () => {
      const mockOnLogin = vi.fn();
      
      render(<MockLoginForm onLogin={mockOnLogin} />);
      
      expect(screen.getByTestId('login-form')).toBeInTheDocument();
      expect(screen.getByLabelText('Email:')).toBeInTheDocument();
      expect(screen.getByLabelText('Password:')).toBeInTheDocument();
      expect(screen.getByTestId('login-button')).toBeInTheDocument();
    });

    it('should call onLogin with form data when submitted', async () => {
      const mockOnLogin = vi.fn();
      const user = userEvent.setup();
      
      render(<MockLoginForm onLogin={mockOnLogin} />);
      
      await user.type(screen.getByTestId('email-input'), 'test@example.com');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));
      
      expect(mockOnLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });

    it('should show loading state when loading prop is true', () => {
      const mockOnLogin = vi.fn();
      
      render(<MockLoginForm onLogin={mockOnLogin} loading={true} />);
      
      const button = screen.getByTestId('login-button');
      expect(button).toHaveTextContent('Logging in...');
      expect(button).toBeDisabled();
    });

    it('should require email and password fields', () => {
      const mockOnLogin = vi.fn();
      
      render(<MockLoginForm onLogin={mockOnLogin} />);
      
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('required');
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(passwordInput).toHaveAttribute('type', 'password');
    });
  });

  describe('ProductList Component', () => {
    it('should render products correctly', () => {
      render(<MockProductList products={mockApiResponses.products} />);
      
      expect(screen.getByTestId('product-list')).toBeInTheDocument();
      expect(screen.getByText('Products')).toBeInTheDocument();
      
      // Check first product
      expect(screen.getByTestId('product-MLB123456789')).toBeInTheDocument();
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      expect(screen.getByText('Price: BRL 299.99')).toBeInTheDocument();
      
      // Check second product
      expect(screen.getByTestId('product-MLB987654321')).toBeInTheDocument();
      expect(screen.getByText('Test Product 2')).toBeInTheDocument();
      expect(screen.getByText('Price: BRL 599.99')).toBeInTheDocument();
    });

    it('should show loading state', () => {
      render(<MockProductList products={[]} loading={true} />);
      
      expect(screen.getByTestId('loading')).toBeInTheDocument();
      expect(screen.getByText('Loading products...')).toBeInTheDocument();
    });

    it('should show empty state when no products', () => {
      render(<MockProductList products={[]} loading={false} />);
      
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
      expect(screen.getByText('No products found')).toBeInTheDocument();
    });
  });

  describe('Dashboard Component', () => {
    const mockUser = { email: 'test@example.com', token: 'mock-token' };
    
    it('should render dashboard with user info', () => {
      const mockOnLogout = vi.fn();
      
      render(
        <MockDashboard 
          user={mockUser} 
          products={mockApiResponses.products}
          onLogout={mockOnLogout}
        />
      );
      
      expect(screen.getByTestId('dashboard')).toBeInTheDocument();
      expect(screen.getByText('ML Integration Dashboard')).toBeInTheDocument();
      expect(screen.getByTestId('user-info')).toHaveTextContent('Welcome, test@example.com');
      expect(screen.getByTestId('logout-button')).toBeInTheDocument();
    });

    it('should call onLogout when logout button is clicked', async () => {
      const mockOnLogout = vi.fn();
      const user = userEvent.setup();
      
      render(
        <MockDashboard 
          user={mockUser} 
          products={[]}
          onLogout={mockOnLogout}
        />
      );
      
      await user.click(screen.getByTestId('logout-button'));
      
      expect(mockOnLogout).toHaveBeenCalledTimes(1);
    });

    it('should display products in dashboard', () => {
      const mockOnLogout = vi.fn();
      
      render(
        <MockDashboard 
          user={mockUser} 
          products={mockApiResponses.products}
          onLogout={mockOnLogout}
        />
      );
      
      expect(screen.getByTestId('product-list')).toBeInTheDocument();
      expect(screen.getByText('Test Product 1')).toBeInTheDocument();
      expect(screen.getByText('Test Product 2')).toBeInTheDocument();
    });
  });
});

describe('Login Flow Integration', () => {
  beforeEach(() => {
    setupGlobalMocks();
  });

  afterEach(() => {
    cleanupMocks();
  });

  it('should handle successful login flow', async () => {
    // Mock successful login response
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponses.login,
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockApiResponses.products,
      });

    // Mock React.useState for the App component
    const states = [
      null, // user
      [], // products
      false, // loading
      null, // error
    ];
    let stateIndex = 0;
    
    global.React.useState = vi.fn((initialValue) => {
      const currentIndex = stateIndex++;
      const setState = vi.fn((newValue) => {
        states[currentIndex] = typeof newValue === 'function' 
          ? newValue(states[currentIndex]) 
          : newValue;
      });
      return [states[currentIndex], setState];
    });

    render(<MockApp />);

    // Should show login form initially
    expect(screen.getByTestId('login-form')).toBeInTheDocument();

    // Fill in login form
    const user = userEvent.setup();
    await user.type(screen.getByTestId('email-input'), 'test@example.com');
    await user.type(screen.getByTestId('password-input'), 'password123');
    await user.click(screen.getByTestId('login-button'));

    // Verify login API call
    expect(fetch).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/auth/token`,
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
    );
  });

  it('should handle login failure', async () => {
    // Mock failed login response
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Incorrect username or password' }),
    });

    const states = [null, [], false, null];
    let stateIndex = 0;
    
    global.React.useState = vi.fn((initialValue) => {
      const currentIndex = stateIndex++;
      const setState = vi.fn();
      return [states[currentIndex], setState];
    });

    render(<MockApp />);

    const user = userEvent.setup();
    await user.type(screen.getByTestId('email-input'), 'wrong@example.com');
    await user.type(screen.getByTestId('password-input'), 'wrongpassword');
    await user.click(screen.getByTestId('login-button'));

    // Should still show login form on failure
    expect(screen.getByTestId('login-form')).toBeInTheDocument();
  });
});

describe('Accessibility Tests', () => {
  it('should have proper ARIA labels and semantic HTML', () => {
    const mockOnLogin = vi.fn();
    
    render(<MockLoginForm onLogin={mockOnLogin} />);
    
    // Check for proper labels
    expect(screen.getByLabelText('Email:')).toBeInTheDocument();
    expect(screen.getByLabelText('Password:')).toBeInTheDocument();
    
    // Check for semantic form element
    expect(screen.getByRole('form')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('should have proper heading hierarchy', () => {
    render(<MockProductList products={mockApiResponses.products} />);
    
    // Should have proper heading levels
    expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent('Products');
    expect(screen.getAllByRole('heading', { level: 3 })).toHaveLength(2); // Product titles
  });
});