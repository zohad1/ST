import requests
import json

# Test token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0OTIzZGY5MC0wZWNiLTQwZTQtODExNC0wYjJhOTdhMjgwYTMiLCJlbWFpbCI6ImNyZWF0b3JAZXhhbXBsZS5jb20iLCJyb2xlIjoiY3JlYXRvciIsImlhdCI6MTczNDk5NzI5MCwiZXhwIjoxNzM1MDgzNjkwfQ.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

base_url = "http://localhost:8004/api/v1"

# Test endpoints
endpoints = [
    "/payments/overview",
    "/earnings/creator/4923df90-0ecb-40e4-8114-0b2a97a280a3/summary",
    "/payments/history"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        print(f"\n{endpoint}:")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
    except Exception as e:
        print(f"\n{endpoint}: Error - {e}") 