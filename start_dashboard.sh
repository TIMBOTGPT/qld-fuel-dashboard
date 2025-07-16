#!/bin/bash
# Queensland Fuel Price Dashboard Startup Script

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "🚀 Starting Queensland Fuel Price Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:5003"
echo "🛑 Press Ctrl+C to stop the dashboard"
echo ""

python3 qld_fuel_web_app.py