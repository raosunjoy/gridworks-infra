import { test, expect } from '@playwright/test';

test.describe('Developer Portal', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should display developer portal correctly', async ({ page }) => {
    await page.goto('/developer');
    
    // Check page title and header
    await expect(page).toHaveTitle(/TradeMate/);
    await expect(page.getByText('TradeMate Developer Portal')).toBeVisible();
    await expect(page.getByRole('button', { name: /get api key/i })).toBeVisible();
  });

  test('should display navigation tabs', async ({ page }) => {
    await page.goto('/developer');
    
    // Check all navigation tabs
    await expect(page.getByText('Overview')).toBeVisible();
    await expect(page.getByText('API Reference')).toBeVisible();
    await expect(page.getByText('API Sandbox')).toBeVisible();
    await expect(page.getByText('SDKs')).toBeVisible();
    await expect(page.getByText('Webhooks')).toBeVisible();
    await expect(page.getByText('Guides')).toBeVisible();
  });

  test('should switch between tabs', async ({ page }) => {
    await page.goto('/developer');
    
    // Start on Overview tab (default)
    await expect(page.getByRole('button', { name: 'Overview' })).toHaveClass(/border-blue-500/);
    
    // Click API Reference tab
    await page.getByRole('button', { name: 'API Reference' }).click();
    await expect(page.getByRole('button', { name: 'API Reference' })).toHaveClass(/border-blue-500/);
    
    // Click API Sandbox tab
    await page.getByRole('button', { name: 'API Sandbox' }).click();
    await expect(page.getByRole('button', { name: 'API Sandbox' })).toHaveClass(/border-blue-500/);
  });

  test('should display API documentation in API Reference tab', async ({ page }) => {
    await page.goto('/developer');
    
    // Click API Reference tab
    await page.getByRole('button', { name: 'API Reference' }).click();
    
    // Check for API documentation sections
    await expect(page.getByText('Market Data APIs')).toBeVisible();
    await expect(page.getByText('AI Insights APIs')).toBeVisible();
    await expect(page.getByText('WhatsApp Integration')).toBeVisible();
    await expect(page.getByText('Billing & Payments')).toBeVisible();
    await expect(page.getByText('User Management')).toBeVisible();
    await expect(page.getByText('Analytics')).toBeVisible();
  });

  test('should display code examples', async ({ page }) => {
    await page.goto('/developer');
    
    // Click API Reference tab
    await page.getByRole('button', { name: 'API Reference' }).click();
    
    // Look for code examples (they would be in code blocks)
    const codeBlocks = page.locator('pre, code');
    await expect(codeBlocks.first()).toBeVisible();
  });

  test('should display sandbox in API Sandbox tab', async ({ page }) => {
    await page.goto('/developer');
    
    // Click API Sandbox tab
    await page.getByRole('button', { name: 'API Sandbox' }).click();
    
    // Check for sandbox elements
    await expect(page.getByText('API Testing Sandbox')).toBeVisible();
    await expect(page.getByText('Test our APIs in real-time')).toBeVisible();
  });

  test('should display SDKs in SDKs tab', async ({ page }) => {
    await page.goto('/developer');
    
    // Click SDKs tab
    await page.getByRole('button', { name: 'SDKs' }).click();
    
    // Check for SDK information
    await expect(page.getByText('Official SDKs')).toBeVisible();
    await expect(page.getByText('Node.js')).toBeVisible();
    await expect(page.getByText('Python')).toBeVisible();
    await expect(page.getByText('React')).toBeVisible();
    await expect(page.getByText('PHP')).toBeVisible();
  });

  test('should display webhooks configuration', async ({ page }) => {
    await page.goto('/developer');
    
    // Click Webhooks tab
    await page.getByRole('button', { name: 'Webhooks' }).click();
    
    // Check for webhook information
    await expect(page.getByText('Webhook Configuration')).toBeVisible();
    await expect(page.getByText('Real-time Event Notifications')).toBeVisible();
  });

  test('should display guides in Guides tab', async ({ page }) => {
    await page.goto('/developer');
    
    // Click Guides tab
    await page.getByRole('button', { name: 'Guides' }).click();
    
    // Check for guide information
    await expect(page.getByText('Developer Guides')).toBeVisible();
    await expect(page.getByText('Getting Started')).toBeVisible();
    await expect(page.getByText('Authentication & Security')).toBeVisible();
    await expect(page.getByText('WhatsApp Integration')).toBeVisible();
  });

  test('should handle copy code functionality', async ({ page }) => {
    await page.goto('/developer');
    
    // Click API Reference tab
    await page.getByRole('button', { name: 'API Reference' }).click();
    
    // Look for copy buttons (if any)
    const copyButtons = page.getByRole('button', { name: /copy/i });
    if (await copyButtons.count() > 0) {
      await copyButtons.first().click();
      // The copy functionality would update clipboard, but we can't test that directly
      // We can check if the button shows a confirmation state
    }
  });
});

test.describe('Developer Portal - Mobile', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should display correctly on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/developer');
    
    // Check that header is visible
    await expect(page.getByText('TradeMate Developer Portal')).toBeVisible();
    
    // Check that navigation tabs are visible (might be in a different layout)
    await expect(page.getByText('Overview')).toBeVisible();
    await expect(page.getByText('API Reference')).toBeVisible();
  });

  test('should maintain tab functionality on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/developer');
    
    // Test tab switching on mobile
    await page.getByRole('button', { name: 'API Reference' }).click();
    await expect(page.getByRole('button', { name: 'API Reference' })).toHaveClass(/border-blue-500/);
  });
});

test.describe('Developer Portal - Without Authentication', () => {
  test('should redirect to sign-in when not authenticated', async ({ page }) => {
    await page.goto('/developer');
    
    // Should redirect to sign-in page
    await expect(page).toHaveURL(/.*\/auth\/signin/);
  });
});

test.describe('Developer Portal - Accessibility', () => {
  test.use({ storageState: 'e2e/auth/admin-session.json' });

  test('should have proper heading structure', async ({ page }) => {
    await page.goto('/developer');
    
    // Check for proper heading hierarchy
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toHaveText('TradeMate Developer Portal');
    
    // Click API Reference to check section headings
    await page.getByRole('button', { name: 'API Reference' }).click();
    
    const h2Elements = page.getByRole('heading', { level: 2 });
    await expect(h2Elements.first()).toBeVisible();
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/developer');
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    
    // Should focus on first interactive element
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test navigation with Enter key
    await page.getByRole('button', { name: 'API Reference' }).focus();
    await page.keyboard.press('Enter');
    
    await expect(page.getByRole('button', { name: 'API Reference' })).toHaveClass(/border-blue-500/);
  });

  test('should have accessible tab interface', async ({ page }) => {
    await page.goto('/developer');
    
    // Check that tab buttons have proper roles
    const tabButtons = page.getByRole('button').filter({ hasText: /Overview|API Reference|Sandbox|SDKs|Webhooks|Guides/ });
    
    for (let i = 0; i < await tabButtons.count(); i++) {
      const tab = tabButtons.nth(i);
      const textContent = await tab.textContent();
      expect(textContent).toBeTruthy();
    }
  });
});