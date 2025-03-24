#!/bin/bash

# Extract dependencies from pyproject.toml and create requirements.txt
python3 -c "
import toml
with open('pyproject.toml') as f:
    config = toml.load(f)
deps = config['project']['dependencies']
with open('requirements.txt', 'w') as f:
    for dep in deps:
        f.write(f'{dep}\n')
"

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