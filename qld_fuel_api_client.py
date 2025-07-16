#!/usr/bin/env python3
"""
Queensland Fuel Price API Client
Comprehensive client for accessing Queensland fuel price data from multiple sources.
"""

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
from typing import Dict, List, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QLDFuelPriceAPI:
    """
    Queensland Fuel Price API Client
    
    Provides access to:
    1. Live API endpoints from fppdirectapi-prod.fuelpricesqld.com.au
    2. Historical data from Queensland Government Open Data Portal
    3. Data processing and analysis tools
    """
    
    def __init__(self, api_token: str = "b03319f8-7727-493b-9015-b20a7acae110"):
        """
        Initialize the API client
        
        Args:
            api_token: Your Queensland Fuel Prices API token
        """
        self.api_token = api_token
        self.base_url = "https://fppdirectapi-prod.fuelpricesqld.com.au"
        self.headers = {
            'Authorization': f'FPDAPI SubscriberToken={api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'QLD-Fuel-Dashboard/1.0'
        }
        
        # Data storage
        self.fuel_types = None
        self.regions = None
        self.brands = None
        self.sites = None
        self.prices = None
        
        # Cache settings
        self.cache_duration = 300  # 5 minutes
        self.last_cache_time = {}
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling and caching
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data
        """
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Making request to: {url}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"error": f"Invalid JSON response: {e}"}
    
    def get_api_version(self) -> str:
        """Get API version information"""
        try:
            response = requests.get(f"{self.base_url}/Version", headers=self.headers)
            return response.text.strip('"') if response.status_code == 200 else "Unknown"
        except Exception as e:
            logger.error(f"Failed to get API version: {e}")
            return "Unknown"
    
    def get_fuel_types(self, country_id: int = 1) -> Dict:
        """
        Get available fuel types
        
        Args:
            country_id: Country ID (1 for Australia)
            
        Returns:
            Dictionary containing fuel types
        """
        cache_key = f"fuel_types_{country_id}"
        
        if self._is_cached(cache_key):
            return self.fuel_types
            
        data = self._make_request("/Subscriber/GetCountryFuelTypes", {"countryId": country_id})
        
        if "error" not in data:
            self.fuel_types = data
            self._update_cache(cache_key)
            
        return data
    
    def get_geographic_regions(self, country_id: int = 1) -> Dict:
        """
        Get geographic regions
        
        Args:
            country_id: Country ID (1 for Australia)
            
        Returns:
            Dictionary containing geographic regions
        """
        cache_key = f"regions_{country_id}"
        
        if self._is_cached(cache_key):
            return self.regions
            
        data = self._make_request("/Subscriber/GetCountryGeographicRegions", {"countryId": country_id})
        
        if "error" not in data:
            self.regions = data
            self._update_cache(cache_key)
            
        return data
    
    def get_brands(self, country_id: int = 1) -> Dict:
        """
        Get fuel brands
        
        Args:
            country_id: Country ID (1 for Australia)
            
        Returns:
            Dictionary containing fuel brands
        """
        cache_key = f"brands_{country_id}"
        
        if self._is_cached(cache_key):
            return self.brands
            
        data = self._make_request("/Subscriber/GetCountryBrands", {"countryId": country_id})
        
        if "error" not in data:
            self.brands = data
            self._update_cache(cache_key)
            
        return data
    
    def get_site_details(self, country_id: int = 1, geo_region_level: int = 1, geo_region_id: int = 1) -> Dict:
        """
        Get detailed site information
        
        Args:
            country_id: Country ID (1 for Australia)
            geo_region_level: Geographic region level
            geo_region_id: Geographic region ID
            
        Returns:
            Dictionary containing site details
        """
        params = {
            "countryId": country_id,
            "geoRegionLevel": geo_region_level,
            "geoRegionId": geo_region_id
        }
        
        data = self._make_request("/Subscriber/GetFullSiteDetails", params)
        
        if "error" not in data:
            self.sites = data
            
        return data
    
    def get_site_prices(self, country_id: int = 1, geo_region_level: int = 1, geo_region_id: int = 1) -> Dict:
        """
        Get current fuel prices for sites
        
        Args:
            country_id: Country ID (1 for Australia)
            geo_region_level: Geographic region level
            geo_region_id: Geographic region ID
            
        Returns:
            Dictionary containing current prices
        """
        params = {
            "countryId": country_id,
            "geoRegionLevel": geo_region_level,
            "geoRegionId": geo_region_id
        }
        
        data = self._make_request("/Price/GetSitesPrices", params)
        
        if "error" not in data:
            self.prices = data
            
        return data
    
    def download_historical_data(self, year: int = 2025, month: int = 1) -> pd.DataFrame:
        """
        Download historical fuel price data from Queensland Government Open Data Portal
        
        Args:
            year: Year to download data for
            month: Month to download data for (1-12)
            
        Returns:
            Pandas DataFrame with historical data
        """
        # Mapping of available datasets
        datasets = {
            2025: {
                1: "https://www.data.qld.gov.au/dataset/7c07fdce-a5f0-4de0-8213-b8a31575a26d/resource/3d3676f9-9ead-46cb-878b-e5c26f4b14d2/download/fuel-prices-2025-01-changes-only.csv"
            },
            2024: {
                6: "https://www.data.qld.gov.au/dataset/c59ba00b-8d2b-4a61-896c-889e0b926d22/resource/dab7eb50-e789-4be5-a9ad-bacc35d6d50d/download/fuel-prices-june-2024.csv"
            }
        }
        
        try:
            if year in datasets and month in datasets[year]:
                url = datasets[year][month]
                logger.info(f"Downloading historical data from: {url}")
                
                # Handle redirects
                response = requests.get(url, allow_redirects=True, timeout=60)
                response.raise_for_status()
                
                # Check if response is HTML (redirect page)
                if response.headers.get('content-type', '').startswith('text/html'):
                    logger.warning("Got HTML response, attempting to parse redirect...")
                    # Try to extract the actual CSV URL from the redirect page
                    import re
                    csv_url_match = re.search(r'href="([^"]*\.csv[^"]*)"', response.text)
                    if csv_url_match:
                        actual_url = csv_url_match.group(1)
                        logger.info(f"Found actual CSV URL: {actual_url}")
                        response = requests.get(actual_url, timeout=60)
                        response.raise_for_status()
                
                # Parse CSV
                from io import StringIO
                df = pd.read_csv(StringIO(response.text))
                
                # Clean and standardize data
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
        """
        Clean and standardize historical data
        
        Args:
            df: Raw DataFrame from CSV
            
        Returns:
            Cleaned DataFrame
        """
        try:
            # Remove BOM if present
            if df.columns[0].startswith('\ufeff'):
                df.columns = [df.columns[0][1:]] + df.columns[1:].tolist()
            
            # Standardize column names
            column_mapping = {
                'SiteId': 'site_id',
                'Site_Name': 'site_name',
                'Site_Brand': 'site_brand',
                'Sites_Address_Line_1': 'address',
                'Site_Suburb': 'suburb',
                'Site_State': 'state',
                'Site_Post_Code': 'postcode',
                'Site_Latitude': 'latitude',
                'Site_Longitude': 'longitude',
                'Fuel_Type': 'fuel_type',
                'Price': 'price',
                'TransactionDateutc': 'transaction_date'
            }
            
            # Rename columns if they exist
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Convert data types
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                df['price_dollars'] = df['price'] / 100  # Convert cents to dollars
            
            if 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
                df['date'] = df['transaction_date'].dt.date
                df['hour'] = df['transaction_date'].dt.hour
            
            if 'latitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            
            if 'longitude' in df.columns:
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # Remove rows with invalid data
            df = df.dropna(subset=['site_id', 'price', 'fuel_type'])
            
            # Sort by transaction date
            if 'transaction_date' in df.columns:
                df = df.sort_values('transaction_date', ascending=False)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning historical data: {e}")
            return df
    
    def analyze_price_trends(self, df: pd.DataFrame, fuel_type: str = None, suburb: str = None) -> Dict:
        """
        Analyze price trends from historical data
        
        Args:
            df: Historical data DataFrame
            fuel_type: Filter by fuel type (optional)
            suburb: Filter by suburb (optional)
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            # Filter data
            filtered_df = df.copy()
            
            if fuel_type:
                filtered_df = filtered_df[filtered_df['fuel_type'] == fuel_type]
            
            if suburb:
                filtered_df = filtered_df[filtered_df['suburb'] == suburb]
