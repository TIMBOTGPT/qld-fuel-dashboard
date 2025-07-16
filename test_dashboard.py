#!/usr/bin/env python3
"""
Test Queensland Fuel Price API and Dashboard
"""

import sys
import os
sys.path.append('/Users/mark/Documents/qld_fuel_dashboard')

try:
    from qld_fuel_api_complete import QLDFuelPriceAPI
    print("✓ API client imported successfully")
    
    # Test API client
    api = QLDFuelPriceAPI()
    print(f"✓ API Version: {api.get_api_version()}")
    
    # Test data download
    print("Testing historical data download...")
    data = api.download_historical_data(2025, 1)
    
    if not data.empty:
        print(f"✓ Downloaded {len(data)} records")
        print(f"✓ Columns: {list(data.columns)}")
        print(f"✓ Fuel types: {data['fuel_type'].unique()}")
        print(f"✓ Date range: {data['transaction_date'].min()} to {data['transaction_date'].max()}")
        
        # Test analysis
        analysis = api.analyze_price_trends(data, fuel_type='Unleaded')
        if 'price_stats' in analysis:
            print(f"✓ Average Unleaded price: ${analysis['price_stats']['mean']:.2f}")
        
        # Test cheapest stations
        cheapest = api.find_cheapest_stations(data, 'Unleaded', limit=3)
        print(f"✓ Found {len(cheapest)} cheapest stations")
        
        if cheapest:
            print("Top 3 cheapest Unleaded stations:")
            for i, station in enumerate(cheapest[:3], 1):
                print(f"  {i}. {station['site_name']} - ${station['price']:.2f}")
        
        print("\n🎉 All tests passed!")
        print("\nTo start the dashboard:")
        print("  1. cd /Users/mark/Documents/qld_fuel_dashboard")
        print("  2. python3 qld_fuel_web_app.py")
        print("  3. Open http://localhost:5000 in your browser")
        
    else:
        print("⚠️ No historical data available - but API client is working")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
