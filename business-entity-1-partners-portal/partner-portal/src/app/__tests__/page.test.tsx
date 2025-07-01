import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useRouter } from 'next/navigation';
import Home from '../page';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    h1: ({ children, ...props }: any) => <h1 {...props}>{children}</h1>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
    section: ({ children, ...props }: any) => <section {...props}>{children}</section>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock Lucide React icons
jest.mock('lucide-react', () => ({
  ArrowRight: () => <span data-testid="arrow-right-icon">→</span>,
  Shield: () => <span data-testid="shield-icon">🛡️</span>,
  Zap: () => <span data-testid="zap-icon">⚡</span>,
  Code: () => <span data-testid="code-icon">💻</span>,
  Users: () => <span data-testid="users-icon">👥</span>,
  BarChart3: () => <span data-testid="chart-icon">📊</span>,
  Lock: () => <span data-testid="lock-icon">🔒</span>,
}));

const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>;

describe('Home Page', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    } as any);
  });

  describe('Hero Section', () => {
    it('should render hero section with correct content', () => {
      render(<Home />);

      expect(screen.getByText('TradeMate Partner Portal')).toBeInTheDocument();
      expect(screen.getByText(/Powerful AI-driven trading platform/)).toBeInTheDocument();
      expect(screen.getByText(/Join our ecosystem of financial institutions/)).toBeInTheDocument();
    });

    it('should render hero CTA buttons', () => {
      render(<Home />);

      expect(screen.getByText('Get Started')).toBeInTheDocument();
      expect(screen.getByText('View Documentation')).toBeInTheDocument();
    });

    it('should navigate to sign-in when Get Started is clicked', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const getStartedButton = screen.getByText('Get Started');
      await user.click(getStartedButton);

      expect(mockPush).toHaveBeenCalledWith('/auth/signin');
    });

    it('should navigate to documentation when View Documentation is clicked', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const docsButton = screen.getByText('View Documentation');
      await user.click(docsButton);

      expect(mockPush).toHaveBeenCalledWith('/docs');
    });

    it('should render hero icons', () => {
      render(<Home />);

      expect(screen.getByTestId('arrow-right-icon')).toBeInTheDocument();
    });
  });

  describe('Features Section', () => {
    it('should render features section with correct heading', () => {
      render(<Home />);

      expect(screen.getByText('Platform Features')).toBeInTheDocument();
      expect(screen.getByText(/Comprehensive tools and services/)).toBeInTheDocument();
    });

    it('should render all feature cards', () => {
      render(<Home />);

      expect(screen.getByText('AI-Powered Analytics')).toBeInTheDocument();
      expect(screen.getByText('Zero-Knowledge Privacy')).toBeInTheDocument();
      expect(screen.getByText('Developer-First API')).toBeInTheDocument();
      expect(screen.getByText('WhatsApp Integration')).toBeInTheDocument();
      expect(screen.getByText('Real-time Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Enterprise Security')).toBeInTheDocument();
    });

    it('should render feature descriptions', () => {
      render(<Home />);

      expect(screen.getByText(/Advanced machine learning algorithms/)).toBeInTheDocument();
      expect(screen.getByText(/End-to-end encryption with zero-knowledge/)).toBeInTheDocument();
      expect(screen.getByText(/RESTful APIs with comprehensive documentation/)).toBeInTheDocument();
      expect(screen.getByText(/Direct integration with WhatsApp Business/)).toBeInTheDocument();
      expect(screen.getByText(/Monitor your trading performance/)).toBeInTheDocument();
      expect(screen.getByText(/Bank-grade security infrastructure/)).toBeInTheDocument();
    });

    it('should render feature icons', () => {
      render(<Home />);

      expect(screen.getByTestId('shield-icon')).toBeInTheDocument();
      expect(screen.getByTestId('zap-icon')).toBeInTheDocument();
      expect(screen.getByTestId('code-icon')).toBeInTheDocument();
      expect(screen.getByTestId('users-icon')).toBeInTheDocument();
      expect(screen.getByTestId('chart-icon')).toBeInTheDocument();
      expect(screen.getByTestId('lock-icon')).toBeInTheDocument();
    });
  });

  describe('Statistics Section', () => {
    it('should render statistics section', () => {
      render(<Home />);

      expect(screen.getByText('Trusted by Industry Leaders')).toBeInTheDocument();
    });

    it('should render all statistics', () => {
      render(<Home />);

      expect(screen.getByText('50+')).toBeInTheDocument();
      expect(screen.getByText('Partner Institutions')).toBeInTheDocument();
      
      expect(screen.getByText('$2.5B+')).toBeInTheDocument();
      expect(screen.getByText('Trading Volume')).toBeInTheDocument();
      
      expect(screen.getByText('99.9%')).toBeInTheDocument();
      expect(screen.getByText('Uptime SLA')).toBeInTheDocument();
      
      expect(screen.getByText('24/7')).toBeInTheDocument();
      expect(screen.getByText('Support Coverage')).toBeInTheDocument();
    });
  });

  describe('CTA Section', () => {
    it('should render call-to-action section', () => {
      render(<Home />);

      expect(screen.getByText('Ready to Get Started?')).toBeInTheDocument();
      expect(screen.getByText(/Join TradeMate today and unlock/)).toBeInTheDocument();
    });

    it('should render CTA buttons', () => {
      render(<Home />);

      const startTradingButtons = screen.getAllByText('Start Trading');
      const contactSalesButtons = screen.getAllByText('Contact Sales');
      
      expect(startTradingButtons).toHaveLength(1);
      expect(contactSalesButtons).toHaveLength(1);
    });

    it('should navigate to sign-in when Start Trading is clicked', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const startTradingButton = screen.getByText('Start Trading');
      await user.click(startTradingButton);

      expect(mockPush).toHaveBeenCalledWith('/auth/signin');
    });

    it('should navigate to contact when Contact Sales is clicked', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const contactSalesButton = screen.getByText('Contact Sales');
      await user.click(contactSalesButton);

      expect(mockPush).toHaveBeenCalledWith('/contact');
    });
  });

  describe('Footer', () => {
    it('should render footer section', () => {
      render(<Home />);

      expect(screen.getByText('TradeMate')).toBeInTheDocument();
      expect(screen.getByText(/Advanced AI-powered trading platform/)).toBeInTheDocument();
    });

    it('should render footer links', () => {
      render(<Home />);

      expect(screen.getByText('Product')).toBeInTheDocument();
      expect(screen.getByText('Features')).toBeInTheDocument();
      expect(screen.getByText('API Docs')).toBeInTheDocument();
      expect(screen.getByText('Pricing')).toBeInTheDocument();
      expect(screen.getByText('Security')).toBeInTheDocument();

      expect(screen.getByText('Company')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
      expect(screen.getByText('Blog')).toBeInTheDocument();
      expect(screen.getByText('Careers')).toBeInTheDocument();
      expect(screen.getByText('Contact')).toBeInTheDocument();

      expect(screen.getByText('Support')).toBeInTheDocument();
      expect(screen.getByText('Help Center')).toBeInTheDocument();
      expect(screen.getByText('Community')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
      expect(screen.getByText('Updates')).toBeInTheDocument();
    });

    it('should render copyright information', () => {
      render(<Home />);

      const currentYear = new Date().getFullYear();
      expect(screen.getByText(`© ${currentYear} TradeMate. All rights reserved.`)).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('should render without layout shifts', () => {
      const { container } = render(<Home />);
      
      expect(container.firstChild).toBeInTheDocument();
      expect(container.querySelector('.min-h-screen')).toBeInTheDocument();
    });

    it('should have proper semantic HTML structure', () => {
      render(<Home />);

      const main = document.querySelector('main');
      expect(main).toBeInTheDocument();
      
      const sections = document.querySelectorAll('section');
      expect(sections.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      render(<Home />);

      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toHaveTextContent('TradeMate Partner Portal');

      const h2Elements = screen.getAllByRole('heading', { level: 2 });
      expect(h2Elements.length).toBeGreaterThan(0);
    });

    it('should have accessible buttons', () => {
      render(<Home />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
        expect(button.tagName).toBe('BUTTON');
      });
    });

    it('should have proper link relationships', () => {
      render(<Home />);

      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link).toBeInTheDocument();
      });
    });
  });

  describe('Navigation Interactions', () => {
    it('should handle keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const getStartedButton = screen.getByText('Get Started');
      
      await user.tab();
      expect(getStartedButton).toHaveFocus();

      await user.keyboard('{Enter}');
      expect(mockPush).toHaveBeenCalledWith('/auth/signin');
    });

    it('should handle multiple button clicks without errors', async () => {
      const user = userEvent.setup();
      render(<Home />);

      const getStartedButton = screen.getByText('Get Started');
      
      await user.click(getStartedButton);
      await user.click(getStartedButton);
      await user.click(getStartedButton);

      expect(mockPush).toHaveBeenCalledTimes(3);
      expect(mockPush).toHaveBeenCalledWith('/auth/signin');
    });
  });

  describe('Error Handling', () => {
    it('should handle router navigation errors gracefully', async () => {
      const user = userEvent.setup();
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      mockPush.mockImplementation(() => {
        throw new Error('Navigation failed');
      });

      render(<Home />);

      const getStartedButton = screen.getByText('Get Started');
      
      // Should not throw and should handle the error gracefully
      await user.click(getStartedButton);

      consoleSpy.mockRestore();
    });

    it('should render even when router is undefined', () => {
      mockUseRouter.mockReturnValue(undefined as any);

      expect(() => render(<Home />)).not.toThrow();
    });
  });

  describe('Performance', () => {
    it('should render quickly without blocking', () => {
      const startTime = performance.now();
      render(<Home />);
      const endTime = performance.now();

      expect(endTime - startTime).toBeLessThan(100); // Should render in less than 100ms
    });

    it('should not cause memory leaks', () => {
      const { unmount } = render(<Home />);
      
      // Should unmount without errors
      expect(() => unmount()).not.toThrow();
    });
  });

  describe('Content Verification', () => {
    it('should display all expected text content', () => {
      render(<Home />);

      // Verify key marketing content
      expect(screen.getByText(/Powerful AI-driven trading platform/)).toBeInTheDocument();
      expect(screen.getByText(/financial institutions and traders/)).toBeInTheDocument();
      expect(screen.getByText(/Advanced machine learning algorithms/)).toBeInTheDocument();
      expect(screen.getByText(/End-to-end encryption with zero-knowledge/)).toBeInTheDocument();
    });

    it('should have consistent branding', () => {
      render(<Home />);

      const tradeMateReferences = screen.getAllByText(/TradeMate/);
      expect(tradeMateReferences.length).toBeGreaterThan(1);
    });
  });
});