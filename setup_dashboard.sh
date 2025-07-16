#!/bin/bash
# Queensland Fuel Price Dashboard Setup Script for macOS
# This script sets up the complete dashboard environment

set -e  # Exit on any error

echo "🚀 Setting up Queensland Fuel Price Dashboard..."
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only"
    exit 1
fi

# Create project directory
PROJECT_DIR="$HOME/Documents/qld_fuel_dashboard"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

print_status "Created project directory: $PROJECT_DIR"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    print_warning "Install Python 3 using: brew install python3"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
pip install --upgrade pip

# Install required packages
print_status "Installing required Python packages..."
pip install flask flask-cors pandas requests beautifulsoup4 lxml openpyxl

# Create requirements.txt
cat > requirements.txt << EOF
flask==2.3.3
flask-cors==4.0.0
pandas==2.0.3
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
openpyxl==3.1.2
EOF

print_status "Requirements file created"

# Create startup script
cat > start_dashboard.sh << 'EOF'
#!/bin/bash
# Queensland Fuel Price Dashboard Startup Script

# Set working directory
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Start the application
echo "🚀 Starting Queensland Fuel Price Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the dashboard"
echo ""

python3 qld_fuel_web_app.py
EOF

chmod +x start_dashboard.sh
print_status "Startup script created"

# Create a desktop application launcher (optional)
cat > launch_dashboard.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./start_dashboard.sh
EOF

chmod +x launch_dashboard.command
print_status "Desktop launcher created"

# Create configuration file
cat > config.json << 'EOF'
{
  "api_token": "b03319f8-7727-493b-9015-b20a7acae110",
  "base_url": "https://fppdirectapi-prod.fuelpricesqld.com.au",
  "cache_duration": 300,
  "update_interval": 1800,
  "default_fuel_type": "Unleaded",
  "default_limit": 10,
  "export_directory": "exports",
  "log_level": "INFO"
}
EOF

print_status "Configuration file created"

# Create exports directory
mkdir -p exports
print_status "Exports directory created"

# Create templates directory
mkdir -p templates
print_status "Templates directory created"

echo ""
echo "🎉 Setup completed successfully!"
echo "================================================="
echo ""
echo "📂 Project directory: $PROJECT_DIR"
echo ""
echo "📝 Next steps:"
echo "   1. Copy the API client and web app files to this directory"
echo "   2. Copy the HTML template to the templates/ directory"
echo "   3. Run: ./start_dashboard.sh"
echo "   4. Open browser to: http://localhost:5000"
echo ""
echo "💡 Alternative: Double-click 'launch_dashboard.command' in Finder"
echo ""
echo "📋 Available scripts:"
echo "   • ./start_dashboard.sh    - Start the web dashboard"
echo "   • ./launch_dashboard.command - Desktop launcher"
echo ""
echo "📁 Files created:"
echo "   • config.json            - Configuration file"
echo "   • requirements.txt       - Python dependencies"
echo "   • start_dashboard.sh     - Startup script"
echo "   • launch_dashboard.command - Desktop launcher"
echo ""
echo "🔧 API Endpoints (when running):"
echo "   • GET /api/status        - API status"
echo "   • GET /api/data          - Cached fuel data"
echo "   • GET /api/analysis      - Price analysis"
echo "   • GET /api/cheapest      - Cheapest stations"
echo "   • GET /api/export        - Export data"
echo ""
echo "Happy fuel price monitoring! ⛽️"
