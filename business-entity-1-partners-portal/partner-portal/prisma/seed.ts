import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function hashPassword(password: string): Promise<string> {
  return await bcrypt.hash(password, 12);
}

function generateApiKey(): string {
  const prefix = 'tm_';
  const randomString = Array.from({ length: 32 }, () => 
    Math.random().toString(36).charAt(Math.floor(Math.random() * 36))
  ).join('');
  const timestamp = Date.now().toString(36);
  return prefix + randomString + timestamp;
}

async function createSeedData() {
  console.log('🌱 Starting database seeding...');

  // Clear existing data
  await prisma.activity.deleteMany();
  await prisma.apiKey.deleteMany();
  await prisma.subscription.deleteMany();
  await prisma.session.deleteMany();
  await prisma.account.deleteMany();
  await prisma.user.deleteMany();
  await prisma.partner.deleteMany();

  console.log('🗑️  Cleared existing data');

  // Create Partners first
  const partners = await Promise.all([
    // Enterprise Partner
    prisma.partner.create({
      data: {
        id: 'partner_enterprise_001',
        companyName: 'TechCorp Enterprise',
        contactName: 'John Smith',
        contactEmail: 'contact@techcorp.com',
        contactPhone: '+1-555-0101',
        website: 'https://techcorp.com',
        description: 'Leading enterprise technology solutions provider',
        tier: 'BLACK',
        status: 'APPROVED',
        industry: 'Technology',
        companySize: 'ENTERPRISE',
        approvedAt: new Date(),
        approvedBy: 'admin@trademate.com',
      },
    }),
    
    // Medium Partner
    prisma.partner.create({
      data: {
        id: 'partner_fintech_002',
        companyName: 'FinTech Solutions Ltd',
        contactName: 'Sarah Johnson',
        contactEmail: 'info@fintech-solutions.com',
        contactPhone: '+1-555-0202',
        website: 'https://fintech-solutions.com',
        description: 'Innovative financial technology solutions',
        tier: 'ELITE',
        status: 'APPROVED',
        industry: 'Financial Services',
        companySize: 'MEDIUM',
        approvedAt: new Date(),
        approvedBy: 'admin@trademate.com',
      },
    }),
    
    // Small Partner  
    prisma.partner.create({
      data: {
        id: 'partner_startup_003',
        companyName: 'InnovateNow Startup',
        contactName: 'Mike Chen',
        contactEmail: 'founder@innovatenow.co',
        contactPhone: '+1-555-0303',
        website: 'https://innovatenow.co',
        description: 'Disruptive startup in the financial sector',
        tier: 'PRO',
        status: 'APPROVED',
        industry: 'FinTech',
        companySize: 'STARTUP',
        approvedAt: new Date(),
        approvedBy: 'admin@trademate.com',
      },
    }),
  ]);

  console.log(`✅ Created ${partners.length} partners`);

  // Create test users for different roles
  const users = await Promise.all([
    // Super Admin
    prisma.user.create({
      data: {
        id: 'user_superadmin_001',
        name: 'Super Admin',
        email: 'superadmin@trademate.com',
        password: await hashPassword('SuperAdmin123!'),
        role: 'SUPER_ADMIN',
        status: 'ACTIVE',
        emailVerified: new Date(),
      },
    }),

    // Admin
    prisma.user.create({
      data: {
        id: 'user_admin_001',
        name: 'Admin User',
        email: 'admin@trademate.com',
        password: await hashPassword('Admin123!'),
        role: 'ADMIN',
        status: 'ACTIVE',
        emailVerified: new Date(),
      },
    }),

    // Partner Admin for Enterprise
    prisma.user.create({
      data: {
        id: 'user_partner_admin_001',
        name: 'John Smith',
        email: 'john@techcorp.com',
        password: await hashPassword('Partner123!'),
        role: 'PARTNER_ADMIN',
        status: 'ACTIVE',
        emailVerified: new Date(),
        partnerId: partners[0].id,
        companyName: 'TechCorp Enterprise',
      },
    }),

    // Partner User for Enterprise
    prisma.user.create({
      data: {
        id: 'user_partner_001',
        name: 'Jane Doe',
        email: 'jane@techcorp.com',
        password: await hashPassword('User123!'),
        role: 'PARTNER',
        status: 'ACTIVE',
        emailVerified: new Date(),
        partnerId: partners[0].id,
        companyName: 'TechCorp Enterprise',
      },
    }),

    // Developer for Medium Partner
    prisma.user.create({
      data: {
        id: 'user_developer_001',
        name: 'Sarah Johnson',
        email: 'sarah@fintech-solutions.com',
        password: await hashPassword('Dev123!'),
        role: 'DEVELOPER',
        status: 'ACTIVE',
        emailVerified: new Date(),
        partnerId: partners[1].id,
        companyName: 'FinTech Solutions Ltd',
      },
    }),

    // Viewer for Small Partner
    prisma.user.create({
      data: {
        id: 'user_viewer_001',
        name: 'Mike Chen',
        email: 'mike@innovatenow.co',
        password: await hashPassword('View123!'),
        role: 'VIEWER',
        status: 'ACTIVE',
        emailVerified: new Date(),
        partnerId: partners[2].id,
        companyName: 'InnovateNow Startup',
      },
    }),
  ]);

  console.log(`✅ Created ${users.length} users`);

  // Create API Keys for partners
  const apiKeys = await Promise.all([
    // Enterprise API Keys
    prisma.apiKey.create({
      data: {
        id: 'apikey_enterprise_prod',
        name: 'Enterprise Production',
        key: generateApiKey(),
        secret: generateApiKey(),
        partnerId: partners[0].id,
        userId: users[2].id, // Partner Admin
        environment: 'PRODUCTION',
        scopes: JSON.stringify(['market-data', 'whatsapp', 'zero-knowledge', 'analytics']),
        rateLimit: 10000,
      },
    }),

    prisma.apiKey.create({
      data: {
        id: 'apikey_enterprise_sandbox',
        name: 'Enterprise Sandbox',
        key: generateApiKey(),
        secret: generateApiKey(),
        partnerId: partners[0].id,
        userId: users[2].id, // Partner Admin
        environment: 'SANDBOX',
        scopes: JSON.stringify(['market-data', 'whatsapp', 'zero-knowledge']),
        rateLimit: 1000,
      },
    }),

    // Medium Partner API Key
    prisma.apiKey.create({
      data: {
        id: 'apikey_fintech_prod',
        name: 'FinTech Production',
        key: generateApiKey(),
        secret: generateApiKey(),
        partnerId: partners[1].id,
        userId: users[4].id, // Developer
        environment: 'PRODUCTION',
        scopes: JSON.stringify(['market-data', 'whatsapp']),
        rateLimit: 5000,
      },
    }),

    // Small Partner API Key
    prisma.apiKey.create({
      data: {
        id: 'apikey_startup_sandbox',
        name: 'Startup Sandbox',
        key: generateApiKey(),
        secret: generateApiKey(),
        partnerId: partners[2].id,
        userId: users[5].id, // Viewer
        environment: 'SANDBOX',
        scopes: JSON.stringify(['market-data']),
        rateLimit: 500,
      },
    }),
  ]);

  console.log(`✅ Created ${apiKeys.length} API keys`);

  // Create subscriptions
  const subscriptions = await Promise.all([
    // Enterprise Subscription
    prisma.subscription.create({
      data: {
        id: 'sub_enterprise_001',
        partnerId: partners[0].id,
        planName: 'Black Tier Enterprise',
        tier: 'BLACK',
        status: 'ACTIVE',
        billingCycle: 'YEARLY',
        monthlyPrice: 2999.99,
        yearlyPrice: 29999.99,
        requestLimit: 1000000,
        userLimit: 50,
        features: JSON.stringify([
          'unlimited_api_calls',
          'priority_support',
          'custom_integrations',
          'dedicated_account_manager',
          'sla_guarantee'
        ]),
      },
    }),

    // Medium Partner Subscription
    prisma.subscription.create({
      data: {
        id: 'sub_fintech_002',
        partnerId: partners[1].id,
        planName: 'Elite Tier Professional',
        tier: 'ELITE',
        status: 'ACTIVE',
        billingCycle: 'MONTHLY',
        monthlyPrice: 999.99,
        yearlyPrice: 9999.99,
        requestLimit: 250000,
        userLimit: 20,
        features: JSON.stringify([
          'extended_api_access',
          'priority_support',
          'analytics_dashboard',
          'webhook_support'
        ]),
      },
    }),

    // Small Partner Subscription
    prisma.subscription.create({
      data: {
        id: 'sub_startup_003',
        partnerId: partners[2].id,
        planName: 'Pro Tier Starter',
        tier: 'PRO',
        status: 'ACTIVE',
        billingCycle: 'MONTHLY',
        monthlyPrice: 299.99,
        yearlyPrice: 2999.99,
        requestLimit: 50000,
        userLimit: 5,
        features: JSON.stringify([
          'standard_api_access',
          'email_support',
          'basic_analytics'
        ]),
      },
    }),
  ]);

  console.log(`✅ Created ${subscriptions.length} subscriptions`);

  // Create some activity logs
  const activities = await Promise.all([
    prisma.activity.create({
      data: {
        type: 'USER_LOGIN',
        userId: users[2].id,
        partnerId: partners[0].id,
        title: 'User Login',
        description: 'Partner admin logged in successfully',
        ipAddress: '192.168.1.100',
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
      },
    }),

    prisma.activity.create({
      data: {
        type: 'API_KEY_CREATED',
        userId: users[2].id,
        partnerId: partners[0].id,
        title: 'API Key Created',
        description: 'Created new production API key',
        metadata: JSON.stringify({ keyId: apiKeys[0].id }),
      },
    }),

    prisma.activity.create({
      data: {
        type: 'API_CALL',
        userId: users[4].id,
        partnerId: partners[1].id,
        title: 'API Call Made',
        description: 'Market data API called successfully',
        metadata: JSON.stringify({ endpoint: '/api/v1/market-data', responseTime: '120ms' }),
      },
    }),
  ]);

  console.log(`✅ Created ${activities.length} activity logs`);

  console.log(`
🎉 Database seeding completed successfully!

📊 Summary:
• ${partners.length} Partners created
• ${users.length} Users created  
• ${apiKeys.length} API Keys created
• ${subscriptions.length} Subscriptions created
• ${activities.length} Activity logs created

🔐 Test User Credentials:
• Super Admin: superadmin@trademate.com / SuperAdmin123!
• Admin: admin@trademate.com / Admin123!
• Partner Admin: john@techcorp.com / Partner123!
• Partner User: jane@techcorp.com / User123!
• Developer: sarah@fintech-solutions.com / Dev123!
• Viewer: mike@innovatenow.co / View123!
  `);
}

createSeedData()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });