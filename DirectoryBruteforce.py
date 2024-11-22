import requests

def directory_bruteforce(url, wordlist):
    with open(wordlist, "r") as file:
        directories = file.read().splitlines()
    
    for directory in directories:
        full_url = f"{url}/{directory}"
        response = requests.get(full_url)
        if response.status_code == 200:
            print(f"Found directory: {full_url}")

# Example usage
url = "https://example.com"
wordlist = "directory_wordlist.txt"
directory_bruteforce(url, wordlist)