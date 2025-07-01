#!/bin/bash

# Database Setup Script for TradeMate Partner Portal

set -e

echo "🚀 Setting up TradeMate Partner Portal Database..."

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local file not found. Please create it first."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Generate Prisma client
echo "🔧 Generating Prisma client..."
npm run db:generate

# Push database schema (creates tables)
echo "📊 Creating database schema..."
npm run db:push

# Seed the database
echo "🌱 Seeding database with test data..."
npm run db:seed

echo "✅ Database setup completed successfully!"
echo ""
echo "🔑 Test User Credentials:"
echo "  Super Admin: superadmin@trademate.com / SuperAdmin123!"
echo "  Admin: admin@trademate.com / Admin123!"
echo "  Enterprise Admin: john.admin@techcorp.com / Enterprise123!"
echo "  Developer: sarah.dev@techcorp.com / Developer123!"
echo ""
echo "🚀 Start the development server with: npm run dev"
echo "📊 View database with: npm run db:studio"
echo "🌐 Portal will be available at: http://localhost:3001"
echo "🔧 Admin dashboard at: http://localhost:3001/admin"
echo "👨‍💻 Developer portal at: http://localhost:3001/developer"