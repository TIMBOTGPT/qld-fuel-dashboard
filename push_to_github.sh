#!/bin/bash
# Quick GitHub Upload Script
# Run this after creating your repository on GitHub

echo "Enter your GitHub username:"
read github_username

echo "🔗 Setting up remote repository..."
git remote add origin https://github.com/$github_username/qld-fuel-dashboard.git

echo "📤 Pushing to GitHub..."
git push -u origin main

echo "🎉 Upload complete! Check your repository at:"
echo "https://github.com/$github_username/qld-fuel-dashboard"
