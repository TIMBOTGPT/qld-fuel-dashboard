#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
import threading
import time

try:
    from qld_fuel_api_complete import QLDFuelPriceAPI
except ImportError:
    print("API client not found, creating minimal version...")
    
    class QLDFuelPriceAPI:
        def __init__(self):
            pass
            
        def get_api_version(self):
            return "1.0.0"
            
        def download_historical_data(self, year, month):
            return pd.DataFrame()
            
        def get_api_status(self):
            return {'connectivity': 'SIMULATED'}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

fuel_data_cache = {}
last_update_time = None
api_client = None

def initialize_api():
    global api_client
    api_client = QLDFuelPriceAPI()
    logger.info("API client initialized")

def update_data_cache():
    global fuel_data_cache, last_update_time
    
    try:
        logger.info("Updating data cache...")
        historical_data = api_client.download_historical_data(2025, 1)
        
        if not historical_data.empty:
            # Convert to JSON-serializable format, handling NaT values
            historical_records = []
            for _, row in historical_data.iterrows():
                record = row.to_dict()
                
                # Handle NaT values in transaction_date
                if pd.isna(record.get('transaction_date')):
                    record['transaction_date'] = None
                else:
                    record['transaction_date'] = record['transaction_date'].isoformat()
                
                # Handle NaT values in date
                if pd.isna(record.get('date')):
                    record['date'] = None
                else:
                    record['date'] = record['date'].isoformat()
                
                historical_records.append(record)
            
            fuel_data_cache = {
                'historical_data': historical_records,
                'summary_stats': api_client.analyze_price_trends(historical_data),
                'fuel_types': historical_data['fuel_type'].unique().tolist(),
                'suburbs': historical_data['suburb'].unique().tolist(),
                'brands': historical_data['site_brand'].unique().tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            last_update_time = datetime.now()
            logger.info(f"Data cache updated with {len(historical_data)} records")
        else:
            logger.warning("No historical data available")
            
    except Exception as e:
        logger.error(f"Error updating data cache: {e}")
        import traceback
        traceback.print_exc()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    try:
        status = api_client.get_api_status()
        status['cache_last_updated'] = last_update_time.isoformat() if last_update_time else None
        status['cached_records'] = len(fuel_data_cache.get('historical_data', []))
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data')
def get_fuel_data():
    try:
        if (not fuel_data_cache or 
            not last_update_time or 
            datetime.now() - last_update_time > timedelta(hours=1)):
            update_data_cache()
        
        return jsonify(fuel_data_cache)
    except Exception as e:
        logger.error(f"Error getting fuel data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cheapest')
def get_cheapest_stations():
    try:
        fuel_type = request.args.get('fuel_type', 'Unleaded')
        suburb = request.args.get('suburb')
        limit = int(request.args.get('limit', 10))
        
        if not fuel_data_cache.get('historical_data'):
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.DataFrame(fuel_data_cache['historical_data'])
        df['price_dollars'] = pd.to_numeric(df['price_dollars'], errors='coerce')
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
        
        cheapest = api_client.find_cheapest_stations(df, fuel_type, suburb, limit)
        
        return jsonify(cheapest)
    except Exception as e:
        logger.error(f"Error getting cheapest stations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/live')
def get_live_data():
    """Get live data from the API with correct parameters"""
    try:
        # Update API client methods to use correct parameters
        live_data = {}
        
        # Test live API endpoints with corrected parameters
        import requests
        token = api_client.api_token
        base_url = api_client.base_url
        headers = api_client.headers
        
        # Get fuel types
        response = requests.get(f"{base_url}/Subscriber/GetCountryFuelTypes?countryId=21", headers=headers, timeout=10)
        if response.status_code == 200:
            live_data['fuel_types'] = response.json()
        
        # Get brands
        response = requests.get(f"{base_url}/Subscriber/GetCountryBrands?countryId=21", headers=headers, timeout=10)
        if response.status_code == 200:
            live_data['brands'] = response.json()
        
        # Get live prices (sample region)
        response = requests.get(f"{base_url}/Price/GetSitesPrices?countryId=21&geoRegionLevel=3&geoRegionId=1", headers=headers, timeout=10)
        if response.status_code == 200:
            live_data['live_prices'] = response.json()
        
        # Add summary
        live_data['summary'] = {
            'timestamp': datetime.now().isoformat(),
            'api_version': api_client.get_api_version(),
            'status': 'Working with corrected parameters from Postman collection'
        }
        
        return jsonify(live_data)
    except Exception as e:
        logger.error(f"Error getting live data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export')
def export_data():
    """Export data in various formats"""
    try:
        format_type = request.args.get('format', 'json')
        fuel_type = request.args.get('fuel_type')
        suburb = request.args.get('suburb')
        
        if not fuel_data_cache.get('historical_data'):
            return jsonify({'error': 'No data available'}), 404
        
        # Filter data if requested
        data = fuel_data_cache['historical_data'].copy()
        
        if fuel_type:
            data = [record for record in data if record.get('fuel_type') == fuel_type]
        
        if suburb:
            data = [record for record in data if record.get('suburb') == suburb]
        
        if format_type == 'json':
            return jsonify(data)
        elif format_type == 'csv':
            import pandas as pd
            df = pd.DataFrame(data)
            csv_data = df.to_csv(index=False)
            
            # Return CSV with proper headers
            from flask import Response
            return Response(
                csv_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=fuel-prices.csv'}
            )
        else:
            return jsonify({'error': 'Unsupported format. Use json or csv.'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app_dir = os.path.expanduser("~/Documents/qld_fuel_dashboard")
    os.makedirs(os.path.join(app_dir, "templates"), exist_ok=True)
    
    app.template_folder = os.path.join(app_dir, "templates")
    
    initialize_api()
    update_data_cache()
    
    logger.info("Starting Queensland Fuel Price Dashboard...")
    logger.info("Open your browser to: http://localhost:5008")
    
    try:
        app.run(host='0.0.0.0', port=5008, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        
    logger.info("Dashboard shutdown complete")
