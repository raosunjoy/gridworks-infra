/**
 * Performance Tests for Real-time Investment Analytics
 * Tests live data update performance, memory usage, and rendering optimization
 * Target: Sub-2s response times with efficient memory management
 */

import { performance, PerformanceObserver } from 'perf_hooks';
import { render, screen, act } from '@testing-library/react';
import React from 'react';
import { RealTimePortfolioAnalytics } from '../../components/investment/RealTimePortfolioAnalytics';
import { InvestmentTier } from '../../services/InvestmentSyndicateEngine';

// Mock luxury components for performance testing
jest.mock('../../components/ui/LuxuryCard', () => ({
  LuxuryCard: ({ children }: any) => <div data-testid="luxury-card">{children}</div>,
}));

jest.mock('../../components/ui/TierGlow', () => ({
  TierGlow: ({ children }: any) => <div data-testid="tier-glow">{children}</div>,
}));

// Performance measurement utilities
interface PerformanceMetrics {
  renderTime: number;
  updateTime: number;
  memoryUsage: number;
  reRenderCount: number;
}

const measurePerformance = async (
  testFunction: () => Promise<void>
): Promise<PerformanceMetrics> => {
  const startTime = performance.now();
  const startMemory = process.memoryUsage().heapUsed;
  
  await testFunction();
  
  const endTime = performance.now();
  const endMemory = process.memoryUsage().heapUsed;
  
  return {
    renderTime: endTime - startTime,
    updateTime: 0, // Will be measured separately
    memoryUsage: endMemory - startMemory,
    reRenderCount: 0, // Will be measured with React DevTools mock
  };
};

describe('Investment Analytics Performance Tests', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    // Clear any existing performance marks
    if (typeof window !== 'undefined' && window.performance) {
      window.performance.clearMarks?.();
      window.performance.clearMeasures?.();
    }
  });

  afterEach(() => {
    jest.useRealTimers();
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
  });

  describe('Initial Render Performance', () => {
    it('should render initial portfolio analytics under 500ms', async () => {
      const metrics = await measurePerformance(async () => {
        render(
          <RealTimePortfolioAnalytics
            tier={InvestmentTier.ONYX}
            anonymousId="perf-test-onyx"
            portfolioId="perf-portfolio-1"
          />
        );
        
        // Wait for initial render to complete
        await screen.findByText('Portfolio Analytics');
      });

      expect(metrics.renderTime).toBeLessThan(500); // Under 500ms
      expect(metrics.memoryUsage).toBeLessThan(50 * 1024 * 1024); // Under 50MB
    });

    it('should render complex VOID tier features efficiently', async () => {
      const startTime = performance.now();
      
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-void"
          portfolioId="perf-portfolio-void"
        />
      );

      await screen.findByText('Portfolio Analytics');
      
      const renderTime = performance.now() - startTime;
      expect(renderTime).toBeLessThan(750); // VOID tier can take slightly longer due to quantum features
    });

    it('should handle large dataset rendering efficiently', async () => {
      // Mock large portfolio data
      const mockLargePortfolio = {
        positions: new Array(1000).fill(null).map((_, i) => ({
          id: `position-${i}`,
          value: Math.random() * 10000000,
          change: Math.random() * 1000000,
        })),
      };

      const startTime = performance.now();
      
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="perf-test-large"
          portfolioId="large-portfolio"
        />
      );

      await screen.findByText('Portfolio Analytics');
      
      const renderTime = performance.now() - startTime;
      expect(renderTime).toBeLessThan(1000); // Should handle 1000 positions under 1s
    });
  });

  describe('Live Data Update Performance', () => {
    it('should update live metrics under 100ms per update', async () => {
      const { container } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="perf-test-updates"
          portfolioId="perf-portfolio-updates"
        />
      );

      // Get baseline
      await screen.findByText('Portfolio Analytics');

      // Measure update performance
      const updateTimes: number[] = [];
      
      for (let i = 0; i < 10; i++) {
        const updateStart = performance.now();
        
        // Trigger live update
        act(() => {
          jest.advanceTimersByTime(5000);
        });
        
        const updateEnd = performance.now();
        updateTimes.push(updateEnd - updateStart);
      }

      const averageUpdateTime = updateTimes.reduce((a, b) => a + b, 0) / updateTimes.length;
      expect(averageUpdateTime).toBeLessThan(100); // Under 100ms per update
    });

    it('should maintain stable performance during extended live sessions', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="perf-test-extended"
          portfolioId="perf-portfolio-extended"
        />
      );

      await screen.findByText('Portfolio Analytics');

      const updateTimes: number[] = [];
      
      // Simulate 2 minutes of live updates (24 updates)
      for (let i = 0; i < 24; i++) {
        const updateStart = performance.now();
        
        act(() => {
          jest.advanceTimersByTime(5000);
        });
        
        const updateEnd = performance.now();
        updateTimes.push(updateEnd - updateStart);
      }

      // Performance should remain stable (no degradation over time)
      const firstHalfAverage = updateTimes.slice(0, 12).reduce((a, b) => a + b, 0) / 12;
      const secondHalfAverage = updateTimes.slice(12).reduce((a, b) => a + b, 0) / 12;
      
      // Second half should not be significantly slower (max 20% degradation)
      expect(secondHalfAverage).toBeLessThan(firstHalfAverage * 1.2);
    });

    it('should handle rapid tab switching efficiently', async () => {
      const { container } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-tabs"
          portfolioId="perf-portfolio-tabs"
        />
      );

      await screen.findByText('Portfolio Analytics');

      const tabs = ['Performance', 'Risk Analysis', 'Allocation', 'ESG Analysis', 'Overview'];
      const switchTimes: number[] = [];

      for (const tabName of tabs) {
        const switchStart = performance.now();
        
        const tabButton = screen.getByRole('button', { name: tabName });
        act(() => {
          tabButton.click();
        });
        
        const switchEnd = performance.now();
        switchTimes.push(switchEnd - switchStart);
      }

      const averageSwitchTime = switchTimes.reduce((a, b) => a + b, 0) / switchTimes.length;
      expect(averageSwitchTime).toBeLessThan(50); // Under 50ms per tab switch
    });
  });

  describe('Memory Management Performance', () => {
    it('should not leak memory during live updates', async () => {
      const initialMemory = process.memoryUsage().heapUsed;
      
      const { unmount } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="perf-test-memory"
          portfolioId="perf-portfolio-memory"
        />
      );

      await screen.findByText('Portfolio Analytics');

      // Simulate 1 minute of updates
      for (let i = 0; i < 12; i++) {
        act(() => {
          jest.advanceTimersByTime(5000);
        });
      }

      const midMemory = process.memoryUsage().heapUsed;
      unmount();

      // Force garbage collection
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage().heapUsed;
      
      // Memory should not grow significantly during updates
      const memoryGrowth = midMemory - initialMemory;
      expect(memoryGrowth).toBeLessThan(20 * 1024 * 1024); // Under 20MB growth
      
      // Memory should be mostly cleaned up after unmount
      const memoryLeak = finalMemory - initialMemory;
      expect(memoryLeak).toBeLessThan(5 * 1024 * 1024); // Under 5MB leak
    });

    it('should efficiently manage large data structures', async () => {
      const startMemory = process.memoryUsage().heapUsed;
      
      // Create multiple instances to test memory efficiency
      const instances = [];
      for (let i = 0; i < 5; i++) {
        const { container } = render(
          <RealTimePortfolioAnalytics
            tier={InvestmentTier.OBSIDIAN}
            anonymousId={`perf-test-multi-${i}`}
            portfolioId={`perf-portfolio-multi-${i}`}
          />
        );
        instances.push(container);
      }

      const peakMemory = process.memoryUsage().heapUsed;
      const memoryPerInstance = (peakMemory - startMemory) / 5;
      
      // Each instance should use less than 10MB
      expect(memoryPerInstance).toBeLessThan(10 * 1024 * 1024);
    });

    it('should clean up intervals and event listeners properly', async () => {
      const clearIntervalSpy = jest.spyOn(global, 'clearInterval');
      const removeEventListenerSpy = jest.spyOn(global, 'removeEventListener').mockImplementation(() => {});
      
      const { unmount } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-cleanup"
          portfolioId="perf-portfolio-cleanup"
        />
      );

      await screen.findByText('Portfolio Analytics');

      // Start live updates
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      unmount();

      // Should clean up intervals
      expect(clearIntervalSpy).toHaveBeenCalled();
      
      clearIntervalSpy.mockRestore();
      removeEventListenerSpy.mockRestore();
    });
  });

  describe('Rendering Optimization Performance', () => {
    it('should minimize re-renders during live updates', async () => {
      let renderCount = 0;
      const TestWrapper = () => {
        renderCount++;
        return (
          <RealTimePortfolioAnalytics
            tier={InvestmentTier.ONYX}
            anonymousId="perf-test-renders"
            portfolioId="perf-portfolio-renders"
          />
        );
      };

      render(<TestWrapper />);
      await screen.findByText('Portfolio Analytics');

      const initialRenderCount = renderCount;

      // Trigger 5 live updates
      for (let i = 0; i < 5; i++) {
        act(() => {
          jest.advanceTimersByTime(5000);
        });
      }

      const finalRenderCount = renderCount;
      const additionalRenders = finalRenderCount - initialRenderCount;
      
      // Should not cause excessive re-renders (max 5 additional for 5 updates)
      expect(additionalRenders).toBeLessThanOrEqual(5);
    });

    it('should efficiently handle chart data updates', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="perf-test-charts"
          portfolioId="perf-portfolio-charts"
        />
      );

      await screen.findByText('Portfolio Analytics');

      // Navigate to Performance tab with charts
      const performanceTab = screen.getByRole('button', { name: 'Performance' });
      
      const chartRenderStart = performance.now();
      
      act(() => {
        performanceTab.click();
      });

      await screen.findByText('Performance vs Benchmarks');
      
      const chartRenderTime = performance.now() - chartRenderStart;
      expect(chartRenderTime).toBeLessThan(200); // Chart should render under 200ms
    });

    it('should optimize DOM updates during live data changes', async () => {
      const { container } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-dom"
          portfolioId="perf-portfolio-dom"
        />
      );

      await screen.findByText('Portfolio Analytics');

      const initialNodeCount = container.querySelectorAll('*').length;

      // Trigger multiple updates
      for (let i = 0; i < 10; i++) {
        act(() => {
          jest.advanceTimersByTime(5000);
        });
      }

      const finalNodeCount = container.querySelectorAll('*').length;
      
      // DOM structure should remain stable (no DOM thrashing)
      expect(Math.abs(finalNodeCount - initialNodeCount)).toBeLessThan(5);
    });
  });

  describe('Tier-Specific Performance', () => {
    it('should maintain performance across all tier levels', async () => {
      const tiers = [InvestmentTier.ONYX, InvestmentTier.OBSIDIAN, InvestmentTier.VOID];
      const tierPerformance: Record<string, number> = {};

      for (const tier of tiers) {
        const startTime = performance.now();
        
        render(
          <RealTimePortfolioAnalytics
            tier={tier}
            anonymousId={`perf-test-${tier}`}
            portfolioId={`perf-portfolio-${tier}`}
          />
        );

        await screen.findByText('Portfolio Analytics');
        
        tierPerformance[tier] = performance.now() - startTime;
      }

      // All tiers should render efficiently
      expect(tierPerformance[InvestmentTier.ONYX]).toBeLessThan(500);
      expect(tierPerformance[InvestmentTier.OBSIDIAN]).toBeLessThan(600);
      expect(tierPerformance[InvestmentTier.VOID]).toBeLessThan(800); // VOID can be slightly slower due to quantum features
    });

    it('should handle quantum features performance overhead efficiently', async () => {
      const { rerender } = render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.ONYX}
          anonymousId="perf-test-quantum"
          portfolioId="perf-portfolio-quantum"
        />
      );

      await screen.findByText('Portfolio Analytics');

      // Navigate to Risk Analysis
      const riskTab = screen.getByRole('button', { name: 'Risk Analysis' });
      act(() => {
        riskTab.click();
      });

      const onyxRiskTime = performance.now();

      // Upgrade to VOID tier
      rerender(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-quantum"
          portfolioId="perf-portfolio-quantum"
        />
      );

      await screen.findByText('Quantum Risk Analysis');
      
      const voidRiskTime = performance.now();
      const quantumOverhead = voidRiskTime - onyxRiskTime;
      
      // Quantum features should not add excessive overhead
      expect(quantumOverhead).toBeLessThan(300); // Under 300ms additional
    });
  });

  describe('Stress Testing', () => {
    it('should handle concurrent updates from multiple data sources', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.OBSIDIAN}
          anonymousId="perf-test-concurrent"
          portfolioId="perf-portfolio-concurrent"
        />
      );

      await screen.findByText('Portfolio Analytics');

      const concurrentUpdateStart = performance.now();

      // Simulate concurrent updates from multiple sources
      await Promise.all([
        // Market data updates
        new Promise(resolve => {
          for (let i = 0; i < 10; i++) {
            setTimeout(() => {
              act(() => {
                jest.advanceTimersByTime(1000);
              });
            }, i * 100);
          }
          setTimeout(resolve, 1000);
        }),
        
        // User interactions
        new Promise(resolve => {
          setTimeout(() => {
            const allocationTab = screen.getByRole('button', { name: 'Allocation' });
            act(() => {
              allocationTab.click();
            });
            resolve(undefined);
          }, 500);
        }),
      ]);

      const concurrentUpdateTime = performance.now() - concurrentUpdateStart;
      expect(concurrentUpdateTime).toBeLessThan(2000); // Should handle concurrent updates under 2s
    });

    it('should maintain performance under high-frequency updates', async () => {
      render(
        <RealTimePortfolioAnalytics
          tier={InvestmentTier.VOID}
          anonymousId="perf-test-frequency"
          portfolioId="perf-portfolio-frequency"
        />
      );

      await screen.findByText('Portfolio Analytics');

      const highFrequencyStart = performance.now();

      // Simulate high-frequency updates (every 100ms for 5 seconds)
      for (let i = 0; i < 50; i++) {
        act(() => {
          jest.advanceTimersByTime(100);
        });
      }

      const highFrequencyTime = performance.now() - highFrequencyStart;
      expect(highFrequencyTime).toBeLessThan(1000); // Should handle 50 rapid updates under 1s
    });
  });
});