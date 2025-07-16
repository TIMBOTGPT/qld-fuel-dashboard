#!/usr/bin/env python3

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from typing import Dict, List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QLDFuelPriceAPI:
    def __init__(self, api_token: str = "b03319f8-7727-493b-9015-b20a7acae110"):
        self.api_token = api_token
        self.base_url = "https://fppdirectapi-prod.fuelpricesqld.com.au"
        self.headers = {
            'Authorization': f'FPDAPI SubscriberToken={api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'QLD-Fuel-Dashboard/1.0'
        }
        self.cache_duration = 300
        self.last_cache_time = {}
        
    def get_api_version(self) -> str:
        try:
            response = requests.get(f"{self.base_url}/Version", headers=self.headers)
            return response.text.strip('"') if response.status_code == 200 else "Unknown"
        except Exception as e:
            logger.error(f"Failed to get API version: {e}")
            return "Unknown"
        
    def get_fuel_types(self, country_id: int = 21) -> Dict:
        """Get available fuel types (21 = Australia in this API)"""
        cache_key = f"fuel_types_{country_id}"
        if self._is_cached(cache_key):
            return self.fuel_types
        data = self._make_request("/Subscriber/GetCountryFuelTypes", {"countryId": country_id})
        if "error" not in data:
            self.fuel_types = data
            self._update_cache(cache_key)
        return data
    
    def get_geographic_regions(self, country_id: int = 21) -> Dict:
        """Get geographic regions (21 = Australia in this API)"""
        cache_key = f"regions_{country_id}"
        if self._is_cached(cache_key):
            return self.regions
        data = self._make_request("/Subscriber/GetCountryGeographicRegions", {"countryId": country_id})
        if "error" not in data:
            self.regions = data
            self._update_cache(cache_key)
        return data
    
    def get_brands(self, country_id: int = 21) -> Dict:
        """Get fuel brands (21 = Australia in this API)"""
        cache_key = f"brands_{country_id}"
        if self._is_cached(cache_key):
            return self.brands
        data = self._make_request("/Subscriber/GetCountryBrands", {"countryId": country_id})
        if "error" not in data:
            self.brands = data
            self._update_cache(cache_key)
        return data
    
    def get_site_details(self, country_id: int = 21, geo_region_level: int = 3, geo_region_id: int = 1) -> Dict:
        """Get detailed site information using correct parameters"""
        params = {"countryId": country_id, "geoRegionLevel": geo_region_level, "geoRegionId": geo_region_id}
        data = self._make_request("/Subscriber/GetFullSiteDetails", params)
        if "error" not in data:
            self.sites = data
        return data
    
    def get_site_prices(self, country_id: int = 21, geo_region_level: int = 3, geo_region_id: int = 1) -> Dict:
        """Get current fuel prices using correct parameters"""
        params = {"countryId": country_id, "geoRegionLevel": geo_region_level, "geoRegionId": geo_region_id}
        data = self._make_request("/Price/GetSitesPrices", params)
        if "error" not in data:
            self.prices = data
        return data
    
    def download_historical_data(self, year: int = 2025, month: int = 1) -> pd.DataFrame:
        datasets = {
            2025: {
                1: "https://www.data.qld.gov.au/ckan-opendata-attachments-prod/resources/3d3676f9-9ead-46cb-878b-e5c26f4b14d2/fuel-prices-2025-01-changes-only.csv?ETag=80372741f8adf7621a9a6cc916f30b06"
            }
        }
        
        try:
            if year in datasets and month in datasets[year]:
                url = datasets[year][month]
                logger.info(f"Downloading historical data from: {url}")
                
                response = requests.get(url, allow_redirects=True, timeout=60)
                response.raise_for_status()
                
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                df = self._clean_historical_data(df)
                
                logger.info(f"Successfully downloaded {len(df)} records")
                return df
            else:
                logger.warning(f"No dataset available for {year}-{month:02d}")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to download historical data: {e}")
            return pd.DataFrame()
    
    def _clean_historical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            if df.columns[0].startswith('\ufeff'):
                df.columns = [df.columns[0][1:]] + df.columns[1:].tolist()
            
            column_mapping = {
                'SiteId': 'site_id', 'Site_Name': 'site_name', 'Site_Brand': 'site_brand',
                'Sites_Address_Line_1': 'address', 'Site_Suburb': 'suburb', 'Site_State': 'state',
                'Site_Post_Code': 'postcode', 'Site_Latitude': 'latitude', 'Site_Longitude': 'longitude',
                'Fuel_Type': 'fuel_type', 'Price': 'price', 'TransactionDateutc': 'transaction_date'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                # Queensland fuel price data appears to be in tenths of cents
                # e.g., 1940 = $1.940 per liter (194.0 cents = $1.94)
                df['price_dollars'] = df['price'] / 1000
            
            if 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
                df['date'] = df['transaction_date'].dt.date
            
            df = df.dropna(subset=['site_id', 'price', 'fuel_type'])
            df = df.sort_values('transaction_date', ascending=False)
            
            return df
        except Exception as e:
            logger.error(f"Error cleaning historical data: {e}")
            return df
    
    def analyze_price_trends(self, df: pd.DataFrame, fuel_type: str = None, suburb: str = None) -> Dict:
        try:
            filtered_df = df.copy()
            
            if fuel_type:
                filtered_df = filtered_df[filtered_df['fuel_type'] == fuel_type]
            if suburb:
                filtered_df = filtered_df[filtered_df['suburb'] == suburb]
                
            if filtered_df.empty:
                return {"error": "No data found for the specified filters"}
            
            # Handle NaT values in date columns
            valid_dates = filtered_df['transaction_date'].dropna()
            
            analysis = {
                'total_records': len(filtered_df),
                'unique_stations': filtered_df['site_id'].nunique(),
                'date_range': {
                    'start': valid_dates.min().strftime('%Y-%m-%d') if not valid_dates.empty else 'Unknown',
                    'end': valid_dates.max().strftime('%Y-%m-%d') if not valid_dates.empty else 'Unknown'
                },
                'price_stats': {
                    'min': filtered_df['price_dollars'].min(),
                    'max': filtered_df['price_dollars'].max(),
                    'mean': filtered_df['price_dollars'].mean(),
                    'median': filtered_df['price_dollars'].median(),
                    'std': filtered_df['price_dollars'].std()
                }
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing price trends: {e}")
            return {"error": str(e)}
    
    def find_cheapest_stations(self, df: pd.DataFrame, fuel_type: str, suburb: str = None, limit: int = 10) -> List[Dict]:
        try:
            filtered_df = df[df['fuel_type'] == fuel_type].copy()
            
            if suburb:
                filtered_df = filtered_df[filtered_df['suburb'] == suburb]
            
            if filtered_df.empty:
                return []
            
            latest_prices = filtered_df.groupby('site_id').last().reset_index()
            cheapest = latest_prices.nsmallest(limit, 'price_dollars')
            
            result = []
            for _, row in cheapest.iterrows():
                # Handle NaT values in date formatting
                last_updated = 'Unknown'
                if pd.notna(row['transaction_date']):
                    last_updated = row['transaction_date'].strftime('%Y-%m-%d %H:%M:%S')
                
                result.append({
                    'site_id': row['site_id'],
                    'site_name': row['site_name'],
                    'brand': row['site_brand'],
                    'address': row['address'],
                    'suburb': row['suburb'],
                    'postcode': row['postcode'],
                    'price': row['price_dollars'],
                    'last_updated': last_updated,
                    'latitude': row['latitude'],
                    'longitude': row['longitude']
                })
            
            return result
        except Exception as e:
            logger.error(f"Error finding cheapest stations: {e}")
            return []
    
    def get_api_status(self) -> Dict:
        status = {
            'timestamp': datetime.now().isoformat(),
            'api_version': self.get_api_version(),
            'endpoints': {
                'base_url': self.base_url,
                'available_endpoints': [
                    '/Version', '/Price/GetSitesPrices', '/Subscriber/GetCountryFuelTypes',
                    '/Subscriber/GetCountryGeographicRegions', '/Subscriber/GetCountryBrands',
                    '/Subscriber/GetFullSiteDetails'
                ]
            }
        }
        
        try:
            response = requests.get(f"{self.base_url}/Version", headers=self.headers, timeout=10)
            status['connectivity'] = 'OK' if response.status_code == 200 else 'ERROR'
        except Exception as e:
            status['connectivity'] = f'ERROR: {e}'
        
        return status

def main():
    api = QLDFuelPriceAPI()
    
    print("=== Queensland Fuel Price API Client ===")
    print(f"API Version: {api.get_api_version()}")
    
    status = api.get_api_status()
    print(f"Connection Status: {status['connectivity']}")
    
    print("\n=== Downloading Historical Data ===")
    historical_data = api.download_historical_data(2025, 1)
    
    if not historical_data.empty:
        print(f"Downloaded {len(historical_data)} records")
        
        analysis = api.analyze_price_trends(historical_data, fuel_type='Unleaded')
        print(f"Average Unleaded price: ${analysis['price_stats']['mean']:.2f}")
        
        cheapest = api.find_cheapest_stations(historical_data, 'Unleaded', limit=5)
        print("\n=== Cheapest Unleaded Stations ===")
        for station in cheapest:
            print(f"{station['site_name']} ({station['brand']}) - ${station['price']:.2f}")
    else:
        print("No historical data available")

if __name__ == "__main__":
    main()
