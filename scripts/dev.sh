#!/bin/bash

# Development startup script for Supply Chain API

echo "🚀 Starting Supply Chain API in development mode..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"
echo "✅ npm version: $(npm -v)"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created from .env.example"
    else
        echo "❌ .env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

# Check if data directory exists
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
    echo "✅ Data directory created"
fi

# Check if data files exist
if [ ! -f "data/dashboard/overview.json" ]; then
    echo "⚠️  Sample data files not found. Please ensure the data directory contains the required JSON files."
    echo "   Expected files:"
    echo "   - data/dashboard/overview.json"
    echo "   - data/threats.json"
    echo "   - data/vendors.json"
    echo "   - data/analytics.json"
    echo "   - data/threats/RPT001.json"
    echo "   - data/threats/RPT002.json"
    echo "   - data/threats/RPT003.json"
    echo "   - data/vendors/V001.json"
    echo "   - data/vendors/V002.json"
    echo "   - data/vendors/V003.json"
fi

echo ""
echo "🔧 Starting development server..."
echo "   API will be available at: http://localhost:8080"
echo "   Health check: http://localhost:8080/api/health"
echo "   WebSocket: ws://localhost:8080/ws"
echo ""

# Start the development server
npm run dev
