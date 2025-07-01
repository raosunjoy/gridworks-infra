import { chromium, FullConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting E2E test setup...');
  
  try {
    // Reset and seed the test database
    console.log('🌱 Setting up test database...');
    await execAsync('npm run db:reset');
    console.log('✅ Test database ready');
    
    // Create admin session for authenticated tests
    console.log('🔑 Creating admin session...');
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate to sign-in page
    await page.goto('http://localhost:3001/auth/signin');
    
    // Sign in as admin
    await page.fill('[name="email"]', 'admin@trademate.com');
    await page.fill('[name="password"]', 'Admin123!');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Save authentication state
    await context.storageState({ path: 'e2e/auth/admin-session.json' });
    
    await browser.close();
    console.log('✅ Admin session created');
    
    // Create partner session
    console.log('🔑 Creating partner session...');
    const partnerBrowser = await chromium.launch();
    const partnerContext = await partnerBrowser.newContext();
    const partnerPage = await partnerContext.newPage();
    
    await partnerPage.goto('http://localhost:3001/auth/signin');
    await partnerPage.fill('[name="email"]', 'john.admin@techcorp.com');
    await partnerPage.fill('[name="password"]', 'Enterprise123!');
    await partnerPage.click('button[type="submit"]');
    
    await partnerPage.waitForURL('**/dashboard', { timeout: 10000 });
    await partnerContext.storageState({ path: 'e2e/auth/partner-session.json' });
    
    await partnerBrowser.close();
    console.log('✅ Partner session created');
    
    console.log('🎉 E2E test setup completed successfully!');
    
  } catch (error) {
    console.error('❌ E2E test setup failed:', error);
    throw error;
  }
}

export default globalSetup;