import requests

def csrf_tester(url, data):
    response = requests.post(url, data=data)
    if "success" in response.text.lower():
        print("CSRF vulnerability found")
    else:
        print("No CSRF vulnerability found")

# Example usage
url = "https://example.com/update"
data = {"username": "admin", "password": "password"}
csrf_tester(url, data)