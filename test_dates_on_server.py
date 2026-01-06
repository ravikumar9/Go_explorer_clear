#!/usr/bin/env python3
"""Test date inputs on server"""
import requests
from bs4 import BeautifulSoup

# Test homepage
response = requests.get('http://goexplorer-dev.cloud/')
soup = BeautifulSoup(response.text, 'html.parser')

# Find date inputs
date_inputs = soup.find_all('input', {'type': 'date'})
print(f"\nFound {len(date_inputs)} date inputs on homepage")

for inp in date_inputs:
    print(f"  - ID: {inp.get('id')}, Name: {inp.get('name')}, Value: {inp.get('value')}, Class: {inp.get('class')}")

# Check if dates are visible CSS
style_tags = soup.find_all('style')
date_style_found = False
for style in style_tags:
    if 'input[type="date"]' in style.text:
        date_style_found = True
        print(f"\n✓ Found date input styles")
        # Print relevant lines
        for line in style.text.split('\n'):
            if 'date' in line.lower() and ('color' in line or 'background' in line):
                print(f"  {line.strip()}")

if not date_style_found:
    print("\n✗ No date input styles found")

# Test hotel list page
print("\n" + "="*50)
response = requests.get('http://goexplorer-dev.cloud/hotels/')
soup = BeautifulSoup(response.text, 'html.parser')
date_inputs = soup.find_all('input', {'type': 'date'})
print(f"\nFound {len(date_inputs)} date inputs on hotels page")

for inp in date_inputs:
    print(f"  - ID: {inp.get('id')}, Name: {inp.get('name')}, Value: {inp.get('value')}")
