import requests

def fuzzer(url, payloads):
    for payload in payloads:
        response = requests.get(url + payload)
        if response.status_code == 200:
            print(f"Fuzzing found: {payload}")

# Example usage
url = "https://example.com/"
payloads = ["admin", "test", "user", "guest"]
fuzzer(url, payloads)