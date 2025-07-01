import { test, expect } from '@playwright/test';

test.describe('Dashboard - Admin User', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should display admin dashboard correctly', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check page title and header
    await expect(page).toHaveTitle(/TradeMate/);
    await expect(page.getByText('TradeMate Portal')).toBeVisible();
    await expect(page.getByText('Welcome back, Admin')).toBeVisible();
    
    // Check user info
    await expect(page.getByText('Admin Manager')).toBeVisible();
    await expect(page.getByText('admin@trademate.com')).toBeVisible();
  });

  test('should display key metrics', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check metric cards
    await expect(page.getByText('API Calls')).toBeVisible();
    await expect(page.getByText('Active Users')).toBeVisible();
    await expect(page.getByText('Revenue')).toBeVisible();
    await expect(page.getByText('Uptime')).toBeVisible();
    
    // Check metric values
    await expect(page.getByText('12.4K')).toBeVisible();
    await expect(page.getByText('1,284')).toBeVisible();
    await expect(page.getByText('₹85.2K')).toBeVisible();
    await expect(page.getByText('99.9%')).toBeVisible();
  });

  test('should display API management section', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page.getByText('API Management')).toBeVisible();
    await expect(page.getByText('Monitor your API usage, manage keys, and view integration status.')).toBeVisible();
    await expect(page.getByText('View API Documentation')).toBeVisible();
    await expect(page.getByText('Manage API Keys')).toBeVisible();
    await expect(page.getByText('Usage Analytics')).toBeVisible();
  });

  test('should display system health section', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page.getByText('System Health')).toBeVisible();
    await expect(page.getByText('API Service')).toBeVisible();
    await expect(page.getByText('Database')).toBeVisible();
    await expect(page.getByText('Cache')).toBeVisible();
    
    // Check health statuses
    const healthyItems = page.getByText('Healthy');
    await expect(healthyItems.first()).toBeVisible();
    await expect(page.getByText('Degraded')).toBeVisible();
  });

  test('should display recent activity', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page.getByText('Recent Activity')).toBeVisible();
    await expect(page.getByText('API key generated')).toBeVisible();
    await expect(page.getByText('WhatsApp integration tested')).toBeVisible();
    await expect(page.getByText('Rate limit warning')).toBeVisible();
    await expect(page.getByText('User authentication successful')).toBeVisible();
  });

  test('should navigate to developer portal', async ({ page }) => {
    await page.goto('/dashboard');
    
    await page.getByText('View API Documentation').click();
    await expect(page).toHaveURL(/.*\/developer/);
    await expect(page.getByText('TradeMate Developer Portal')).toBeVisible();
  });

  test('should navigate to self-healing dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    
    await page.getByText('View Self-Healing Dashboard').click();
    await expect(page).toHaveURL(/.*\/dashboard\/health/);
  });
});

test.describe('Dashboard - Partner User', () => {
  test.use({ storageState: 'e2e/auth/partner-session.json' });

  test('should display partner dashboard correctly', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check welcome message for partner
    await expect(page.getByText('Welcome back, John')).toBeVisible();
    await expect(page.getByText('john.admin@techcorp.com')).toBeVisible();
  });

  test('should show partner-specific metrics', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Partner should see the same metric structure but potentially different values
    await expect(page.getByText('API Calls')).toBeVisible();
    await expect(page.getByText('Active Users')).toBeVisible();
    await expect(page.getByText('Revenue')).toBeVisible();
    await expect(page.getByText('Uptime')).toBeVisible();
  });
});

test.describe('Dashboard - Mobile View', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should display correctly on mobile', async ({ page, browserName }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Check that content is still visible and properly arranged
    await expect(page.getByText('TradeMate Portal')).toBeVisible();
    await expect(page.getByText('Welcome back, Admin')).toBeVisible();
    
    // Check that metric cards stack properly on mobile
    await expect(page.getByText('API Calls')).toBeVisible();
    await expect(page.getByText('Active Users')).toBeVisible();
  });

  test('should maintain functionality on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/dashboard');
    
    // Test navigation still works
    await page.getByText('View API Documentation').click();
    await expect(page).toHaveURL(/.*\/developer/);
  });
});

test.describe('Dashboard - Accessibility', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should have proper heading structure', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for proper heading hierarchy
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toHaveText('TradeMate Portal');
    
    const h2 = page.getByRole('heading', { level: 2 });
    await expect(h2).toHaveText(/Welcome back/);
    
    const h3Elements = page.getByRole('heading', { level: 3 });
    await expect(h3Elements.first()).toBeVisible();
  });

  test('should have accessible buttons and links', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check that all interactive elements are properly labeled
    const buttons = page.getByRole('button');
    for (let i = 0; i < await buttons.count(); i++) {
      const button = buttons.nth(i);
      const ariaLabel = await button.getAttribute('aria-label');
      const textContent = await button.textContent();
      
      // Button should have either aria-label or text content
      expect(ariaLabel || textContent).toBeTruthy();
    }
    
    // Check links
    const links = page.getByRole('link');
    for (let i = 0; i < await links.count(); i++) {
      const link = links.nth(i);
      const href = await link.getAttribute('href');
      expect(href).toBeTruthy();
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Should focus on first interactive element
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test that Enter key works on focused buttons
    const apiDocsLink = page.getByText('View API Documentation');
    await apiDocsLink.focus();
    await page.keyboard.press('Enter');
    
    await expect(page).toHaveURL(/.*\/developer/);
  });
});