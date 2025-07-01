import { FullConfig } from '@playwright/test';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting E2E test teardown...');
  
  try {
    // Clean up authentication files
    const authDir = path.join(__dirname, 'auth');
    try {
      await fs.rm(authDir, { recursive: true, force: true });
      console.log('✅ Authentication files cleaned up');
    } catch (error) {
      console.log('⚠️  No authentication files to clean up');
    }
    
    // Clean up test artifacts
    const testArtifacts = [
      'test-results',
      'playwright-report',
      'screenshots',
      'videos',
      'traces'
    ];
    
    for (const artifact of testArtifacts) {
      try {
        await fs.rm(artifact, { recursive: true, force: true });
      } catch (error) {
        // Ignore if doesn't exist
      }
    }
    
    console.log('🎉 E2E test teardown completed successfully!');
    
  } catch (error) {
    console.error('❌ E2E test teardown failed:', error);
    // Don't throw - teardown failures shouldn't fail the build
  }
}

export default globalTeardown;