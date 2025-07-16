#!/usr/bin/env python3
"""
Test the Queensland Fuel Prices Live API with correct parameters from Postman collection
"""

import requests
import json

def test_live_api():
    """Test the live API with the correct parameters from the Postman collection"""
    
    token = "b03319f8-7727-493b-9015-b20a7acae110"
    base_url = "https://fppdirectapi-prod.fuelpricesqld.com.au"
    headers = {
        'Authorization': f'FPDAPI SubscriberToken={token}',
        'Content-Type': 'application/json'
    }
    
    print("🔧 Testing Queensland Fuel Prices Live API with correct parameters...")
    print("=" * 70)
    
    # Test endpoints with correct parameters from Postman collection
    tests = [
        {
            "name": "GetCountryFuelTypes",
            "url": f"{base_url}/Subscriber/GetCountryFuelTypes?countryId=21"
        },
        {
            "name": "GetCountryGeographicRegions", 
            "url": f"{base_url}/Subscriber/GetCountryGeographicRegions?countryId=21"
        },
        {
            "name": "GetCountryBrands",
            "url": f"{base_url}/Subscriber/GetCountryBrands?countryId=21"
        },
        {
            "name": "GetFullSiteDetails",
            "url": f"{base_url}/Subscriber/GetFullSiteDetails?countryId=21&geoRegionLevel=3&geoRegionId=1"
        },
        {
            "name": "GetSitesPrices",
            "url": f"{base_url}/Price/GetSitesPrices?countryId=21&geoRegionLevel=3&geoRegionId=1"
        }
    ]
    
    results = {}
    
    for test in tests:
        try:
            print(f"\n🔍 Testing {test['name']}...")
            response = requests.get(test['url'], headers=headers, timeout=30)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if isinstance(data, dict):
                        if data:  # Not empty
                            print(f"   ✅ SUCCESS! Got dictionary with keys: {list(data.keys())}")
                            
                            # Show sample data for each endpoint
                            if test['name'] == 'GetCountryFuelTypes' and 'Fuels' in data:
                                fuels = data['Fuels']
                                if fuels:
                                    print(f"   📊 Found {len(fuels)} fuel types")
                                    for fuel in fuels[:3]:
                                        print(f"      - {fuel}")
                                        
                            elif test['name'] == 'GetCountryGeographicRegions' and 'GeographicRegions' in data:
                                regions = data['GeographicRegions']
                                if regions:
                                    print(f"   📍 Found {len(regions)} geographic regions")
                                    for region in regions[:3]:
                                        print(f"      - Level {region.get('GeographicRegionLevel')}: {region.get('GeographicRegionName')} (ID: {region.get('GeographicRegionId')})")
                                        
                            elif test['name'] == 'GetCountryBrands' and 'Brands' in data:
                                brands = data['Brands']
                                if brands:
                                    print(f"   🏪 Found {len(brands)} brands")
                                    for brand in brands[:5]:
                                        print(f"      - {brand}")
                                        
                            elif test['name'] == 'GetFullSiteDetails' and 'Sites' in data:
                                sites = data['Sites']
                                if sites:
                                    print(f"   ⛽ Found {len(sites)} sites")
                                    for site in sites[:3]:
                                        print(f"      - {site.get('SiteName')} ({site.get('Brand')}) - {site.get('Address')}")
                                        
                            elif test['name'] == 'GetSitesPrices' and 'SitePrices' in data:
                                prices = data['SitePrices']
                                if prices:
                                    print(f"   💰 Found {len(prices)} price records")
                                    for price in prices[:3]:
                                        site_name = price.get('SiteName', 'Unknown')
                                        fuel_type = price.get('FuelType', 'Unknown')
                                        price_val = price.get('Price', 0)
                                        print(f"      - {site_name}: {fuel_type} = ${price_val/1000:.3f}")
                                        
                            results[test['name']] = data
                        else:
                            print(f"   ⚠️  Empty response (but successful)")
                            results[test['name']] = {}
                            
                    elif isinstance(data, list):
                        print(f"   ✅ SUCCESS! Got list with {len(data)} items")
                        if data:
                            print(f"   📋 First item: {data[0]}")
                        results[test['name']] = data
                    else:
                        print(f"   📄 Got: {type(data)} = {data}")
                        results[test['name']] = data
                        
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response.text[:200]}")
                    results[test['name']] = {"error": "Invalid JSON"}
                    
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
                results[test['name']] = {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            results[test['name']] = {"error": str(e)}
    
    print("\n" + "=" * 70)
    print("🎯 SUMMARY:")
    
    working_endpoints = []
    for name, result in results.items():
        if isinstance(result, dict) and "error" not in result and result:
            working_endpoints.append(name)
            print(f"✅ {name}: Working with data")
        elif isinstance(result, list) and result:
            working_endpoints.append(name)
            print(f"✅ {name}: Working with data")
        elif isinstance(result, dict) and not result:
            print(f"⚠️  {name}: Working but empty")
        else:
            print(f"❌ {name}: Failed")
    
    print(f"\n🎉 {len(working_endpoints)}/{len(tests)} endpoints working successfully!")
    
    if working_endpoints:
        print("\n💡 Recommended next steps:")
        print("1. Update API client to use countryId=21")
        print("2. Use geoRegionLevel=3&geoRegionId=1 for live data")
        print("3. Integrate live data with historical data in dashboard")
        
    return results

if __name__ == "__main__":
    test_live_api()
