import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should redirect to sign-in when not authenticated', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*\/auth\/signin/);
  });

  test('should display sign-in form correctly', async ({ page }) => {
    await page.goto('/auth/signin');
    
    // Check page title and heading
    await expect(page).toHaveTitle(/TradeMate/);
    await expect(page.getByText('Welcome back')).toBeVisible();
    await expect(page.getByText('Sign in to your partner account')).toBeVisible();
    
    // Check form elements
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    
    // Check social sign-in buttons
    await expect(page.getByRole('button', { name: /google/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /github/i })).toBeVisible();
    
    // Check navigation links
    await expect(page.getByText('Forgot password?')).toBeVisible();
    await expect(page.getByText('Sign up for free')).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/auth/signin');
    
    // Try to submit empty form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Check for HTML5 validation (required fields)
    const emailInput = page.getByLabel('Email address');
    const passwordInput = page.getByLabel('Password');
    
    await expect(emailInput).toHaveAttribute('required');
    await expect(passwordInput).toHaveAttribute('required');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/auth/signin');
    
    // Fill with invalid credentials
    await page.fill('[name="email"]', 'invalid@example.com');
    await page.fill('[name="password"]', 'wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Wait for error message
    await expect(page.getByText(/invalid credentials/i)).toBeVisible({ timeout: 10000 });
  });

  test('should successfully sign in with valid credentials', async ({ page }) => {
    await page.goto('/auth/signin');
    
    // Fill with valid admin credentials
    await page.fill('[name="email"]', 'admin@trademate.com');
    await page.fill('[name="password"]', 'Admin123!');
    
    // Submit form
    await page.getByRole('button', { name: /sign in/i }).click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(/.*\/dashboard/, { timeout: 10000 });
    
    // Should show user info
    await expect(page.getByText('Admin Manager')).toBeVisible();
    await expect(page.getByText('admin@trademate.com')).toBeVisible();
  });

  test('should toggle password visibility', async ({ page }) => {
    await page.goto('/auth/signin');
    
    const passwordInput = page.getByLabel('Password');
    const toggleButton = page.locator('button[type="button"]').last(); // Eye icon button
    
    // Initially password should be hidden
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle to show password
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');
    
    // Click toggle to hide password again
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should navigate to sign-up page', async ({ page }) => {
    await page.goto('/auth/signin');
    
    await page.getByText('Sign up for free').click();
    await expect(page).toHaveURL(/.*\/auth\/signup/);
    
    // Check sign-up page elements
    await expect(page.getByText('Create your account')).toBeVisible();
    await expect(page.getByLabel('Full Name')).toBeVisible();
    await expect(page.getByLabel('Company Name')).toBeVisible();
  });

  test('should navigate to forgot password page', async ({ page }) => {
    await page.goto('/auth/signin');
    
    await page.getByText('Forgot password?').click();
    await expect(page).toHaveURL(/.*\/auth\/forgot-password/);
    
    // Check forgot password page elements
    await expect(page.getByText('Forgot your password?')).toBeVisible();
    await expect(page.getByText('Enter your email and we\'ll send you a reset link')).toBeVisible();
  });
});

test.describe('Sign Up Flow', () => {
  test('should display sign-up form correctly', async ({ page }) => {
    await page.goto('/auth/signup');
    
    // Check form elements
    await expect(page.getByLabel('Full Name')).toBeVisible();
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByLabel('Company Name')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByLabel('Confirm Password')).toBeVisible();
    
    // Check terms checkbox
    await expect(page.getByText(/I agree to the/)).toBeVisible();
    await expect(page.getByText('Terms of Service')).toBeVisible();
    await expect(page.getByText('Privacy Policy')).toBeVisible();
  });

  test('should show password strength indicator', async ({ page }) => {
    await page.goto('/auth/signup');
    
    const passwordInput = page.getByLabel('Password');
    
    // Type weak password
    await passwordInput.fill('weak');
    await expect(page.getByText('Weak')).toBeVisible();
    
    // Type strong password
    await passwordInput.fill('StrongPassword123!');
    await expect(page.getByText('Strong')).toBeVisible();
  });

  test('should show password match validation', async ({ page }) => {
    await page.goto('/auth/signup');
    
    const passwordInput = page.getByLabel('Password');
    const confirmPasswordInput = page.getByLabel('Confirm Password');
    
    // Fill matching passwords
    await passwordInput.fill('TestPassword123!');
    await confirmPasswordInput.fill('TestPassword123!');
    await expect(page.getByText('Passwords match')).toBeVisible();
    
    // Fill non-matching passwords
    await confirmPasswordInput.fill('DifferentPassword123!');
    await expect(page.getByText('Passwords do not match')).toBeVisible();
  });

  test('should require terms agreement', async ({ page }) => {
    await page.goto('/auth/signup');
    
    const submitButton = page.getByRole('button', { name: /create account/i });
    
    // Initially button should be disabled
    await expect(submitButton).toBeDisabled();
    
    // Check terms checkbox
    await page.getByRole('checkbox').check();
    await expect(submitButton).not.toBeDisabled();
  });
});

test.describe('Forgot Password Flow', () => {
  test('should display forgot password form', async ({ page }) => {
    await page.goto('/auth/forgot-password');
    
    await expect(page.getByText('Forgot your password?')).toBeVisible();
    await expect(page.getByLabel('Email address')).toBeVisible();
    await expect(page.getByRole('button', { name: /send reset link/i })).toBeVisible();
    await expect(page.getByText('Back to sign in')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/auth/forgot-password');
    
    const emailInput = page.getByLabel('Email address');
    await expect(emailInput).toHaveAttribute('type', 'email');
    await expect(emailInput).toHaveAttribute('required');
  });

  test('should navigate back to sign in', async ({ page }) => {
    await page.goto('/auth/forgot-password');
    
    await page.getByText('Back to sign in').click();
    await expect(page).toHaveURL(/.*\/auth\/signin/);
  });
});