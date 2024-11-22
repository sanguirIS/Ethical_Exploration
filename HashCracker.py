import hashlib

def hash_cracker(hash_value, wordlist):
    with open(wordlist, "r") as file:
        passwords = file.read().splitlines()
    
    for password in passwords:
        hash_obj = hashlib.md5(password.encode())
        hashed_password = hash_obj.hexdigest()
        if hashed_password == hash_value:
            print(f"Password found: {password}")
            break

# Example usage
hash_value = "5f4dcc3b5aa765d61d8327deb882cf99"
wordlist = "password_list.txt"
hash_cracker(hash_value, wordlist)