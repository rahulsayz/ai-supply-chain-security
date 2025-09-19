#!/bin/bash

# Production build script for Supply Chain API

echo "🏗️  Building Supply Chain API for production..."

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

# Clean previous build
echo "🧹 Cleaning previous build..."
npm run clean
if [ $? -ne 0 ]; then
    echo "❌ Failed to clean previous build"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Run linting
echo "🔍 Running linting..."
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Please fix the issues before building."
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
npm test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Please fix the issues before building."
    exit 1
fi

# Build the project
echo "🔨 Building TypeScript..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build directory 'dist' not found"
    exit 1
fi

# Verify key files exist
REQUIRED_FILES=("dist/server.js" "dist/server.js.map")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required build file not found: $file"
        exit 1
    fi
done

echo ""
echo "✅ Build completed successfully!"
echo "📁 Build output: ./dist/"
echo "🚀 To start the production server: npm start"
echo "🐳 To build Docker image: docker build -t supply-chain-api ."
echo ""

# Show build size
BUILD_SIZE=$(du -sh dist | cut -f1)
echo "📊 Build size: $BUILD_SIZE"

# Show file count
FILE_COUNT=$(find dist -type f | wc -l)
echo "📄 Files generated: $FILE_COUNT"
