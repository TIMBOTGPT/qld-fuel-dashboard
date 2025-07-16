# Queensland Fuel Price Dashboard 🇦🇺⛽️

A comprehensive web-based dashboard for monitoring and analyzing fuel prices across Queensland, Australia. This project integrates historical government data with real-time API feeds to provide users with detailed fuel price insights, station comparisons, and data export capabilities.

![Dashboard Preview](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.1-red)
![Data](https://img.shields.io/badge/Records-54%2C728%2B-orange)

## 🎯 Features

### 📊 **Data Integration**
- **54,728+ historical records** from Queensland Government Open Data Portal
- **6,871+ live price records** from Queensland Fuel Prices API
- **2,681 unique fuel stations** across 705 Queensland suburbs
- **17 fuel types** monitored (Unleaded, Diesel, E10, Premium, LPG, etc.)
- **50 fuel brands** tracked (BP, Shell, Caltex, 7-Eleven, etc.)

### 🌐 **Interactive Web Dashboard**
- Real-time fuel price statistics and trends
- Interactive filtering by fuel type and location
- Search functionality for specific stations
- Find cheapest stations with one click
- Professional, responsive design optimized for all devices

### 🔧 **API & Data Export**
- RESTful API with comprehensive endpoints
- JSON and CSV export capabilities
- Real-time data caching with background updates
- Complete API documentation and testing suite

## 🚀 Quick Start

### Prerequisites
- **macOS 15+** (M1 ARM architecture supported)
- **Python 3.8+**
- **Internet connection** for data downloads

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/qld-fuel-dashboard.git
cd qld-fuel-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python3 test_dashboard.py

# Start the dashboard
python3 qld_fuel_web_app.py
```

### Access Dashboard
Open your browser to: **http://localhost:5008**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Browser Client                       │
│                  (http://localhost:5008)                   │
└─────────────────────┬───────────────────────────────────────┘
                     │ HTTP Requests
┌─────────────────────▼───────────────────────────────────────┐
│                Flask Web Server                            │
│              (qld_fuel_web_app.py)                         │
│     REST API + Dashboard Interface + Data Caching         │
└─────────────────────┬───────────────────────────────────────┘
                     │
┌─────────────────────▼───────────────────────────────────────┐
│               API Client Library                           │
│            (qld_fuel_api_complete.py)                      │
│     Historical Data + Live API + Data Processing          │
└─────────────┬───────────────────────┬─────────────────────┘
              │                       │
┌─────────────▼───────────────┐      ┌▼─────────────────────┐
│     Queensland Fuel         │      │  Queensland Gov      │
│     Prices Live API         │      │  Open Data Portal    │
│                             │      │                      │
│ • 17 fuel types             │      │ • Historical CSV     │
│ • 50 brands                 │      │ • 54,728 records     │
│ • 6,871 live prices         │      │ • Monthly updates    │
│ • Real-time updates         │      │ • Complete coverage  │
└─────────────────────────────┘      └──────────────────────┘
```

## 📁 Project Structure

```
qld-fuel-dashboard/
├── 📄 qld_fuel_api_complete.py      # Main API client library
├── 📄 qld_fuel_web_app.py           # Flask web application
├── 📄 test_dashboard.py             # Installation test script
├── 📄 test_live_api.py              # Live API testing script
├── 📄 setup_dashboard.sh            # Setup script for macOS
├── 📄 start_dashboard.sh            # Startup script
├── 📄 README.md                     # This file
├── 📄 requirements.txt              # Python dependencies
├── 📄 config.json                   # Configuration settings
├── 📁 templates/
│   └── 📄 index.html               # Dashboard interface
├── 📁 exports/                     # Data export directory
└── 📁 venv/                        # Python virtual environment
```

## 🔌 API Endpoints

### Dashboard REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard interface |
| `/api/status` | GET | System status and connectivity |
| `/api/data` | GET | Complete historical fuel data |
| `/api/cheapest` | GET | Find cheapest stations by fuel type |
| `/api/live` | GET | Live API data integration |
| `/api/export` | GET | Export data (JSON/CSV) |

### Example Usage

```bash
# Get system status
curl http://localhost:5008/api/status

# Find cheapest unleaded stations
curl "http://localhost:5008/api/cheapest?fuel_type=Unleaded&limit=10"

# Export data as CSV
curl "http://localhost:5008/api/export?format=csv" > fuel_prices.csv

# Get live API data
curl http://localhost:5008/api/live
```

## 🔧 Configuration

### API Authentication
The system uses the Queensland Fuel Prices API with subscriber token authentication:

```python
# Configuration in config.json
{
  "api_token": "YOUR_SUBSCRIBER_TOKEN",
  "base_url": "https://fppdirectapi-prod.fuelpricesqld.com.au",
  "cache_duration": 300,
  "update_interval": 1800
}
```

### Data Sources
1. **Queensland Government Open Data Portal**
   - Historical CSV data with monthly updates
   - Complete station and price information
   - 54,728+ records available

2. **Queensland Fuel Prices Live API**
   - Real-time price updates
   - 6,871+ current price records
   - Station details and geographic data

## 📊 Data Processing

### Price Conversion
**Critical Discovery:** Queensland data stores prices as **tenths of cents**:
```python
# Correct conversion
price_in_dollars = raw_price / 1000
# Example: 1940 → $1.940 per liter
```

### Data Cleaning Pipeline
1. **Download** - Fetch from government portal
2. **Standardize** - Column mapping and data types
3. **Convert** - Price units and datetime handling
4. **Validate** - Remove invalid records
5. **Cache** - Store for fast access

## 🧪 Testing

```bash
# Test complete installation
python3 test_dashboard.py

# Test live API integration
python3 test_live_api.py

# Validate data processing
python3 -c "from qld_fuel_api_complete import QLDFuelPriceAPI; api = QLDFuelPriceAPI(); print('API Version:', api.get_api_version())"
```

## 🔧 Troubleshooting

### Common Issues

**Port Conflicts:**
```bash
# Kill existing processes
pkill -f qld_fuel_web_app

# Or change port in qld_fuel_web_app.py
app.run(host='0.0.0.0', port=5009, debug=False)
```

**API Authentication:**
- Verify subscriber token in `config.json`
- Check network connectivity
- Ensure correct API parameters (countryId=21)

**Data Issues:**
- Validate price conversion (should be $1.50-$2.50 range)
- Check datetime formatting for NaT values
- Verify CSV download URLs

## 🎯 Key Achievements

- ✅ **Complete API Integration** - All 5 endpoints working
- ✅ **Data Quality** - Proper price conversion and validation
- ✅ **Real-time Updates** - Live data every 30 minutes
- ✅ **Professional Interface** - Responsive web dashboard
- ✅ **Comprehensive Documentation** - Full technical guide
- ✅ **Production Ready** - Error handling and performance optimization

## 🚀 Future Enhancements

- **Geographic Visualization** - Interactive maps with station locations
- **Price Predictions** - Machine learning for price forecasting
- **Mobile App** - React Native companion application
- **Multi-State Support** - Expand to other Australian states
- **Real-time Notifications** - Price alerts and monitoring
- **Advanced Analytics** - Trend analysis and business intelligence

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions, issues, or contributions:
- **Documentation:** Complete technical guide in `/docs/`
- **Issues:** GitHub Issues tab
- **Testing:** Run `test_dashboard.py` for validation

## 🏆 Acknowledgments

- **Queensland Government** for providing open data access
- **Fuel Prices Queensland** for API access and documentation
- **Python Community** for excellent libraries (Flask, Pandas, Requests)

---

**Built with ❤️ for the Queensland community**

*Last Updated: July 17, 2025*
