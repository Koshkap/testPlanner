#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p ./static/dist
mkdir -p ./functions

# Copy static assets
cp -r ./static/* ./static/dist/

# Setup Cloudflare Pages specific structure
cp -r ./templates ./functions/
cp app.py ./functions/
cp auth.py ./functions/

# Set up environment variables
echo "Setting up environment variables..."

# Make the build script executable
chmod +x build.sh