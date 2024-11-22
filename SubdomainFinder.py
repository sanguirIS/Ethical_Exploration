import requests

def subdomain_finder(domain, wordlist):
    with open(wordlist, "r") as file:
        subdomains = file.read().splitlines()
    
    for subdomain in subdomains:
        full_url = f"http://{subdomain}.{domain}"
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                print(f"Found subdomain: {full_url}")
        except:
            pass

# Example usage
domain = "example.com"
wordlist = "subdomain_wordlist.txt"
subdomain_finder(domain, wordlist)