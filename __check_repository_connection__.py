from time import sleep
import requests

def internet_connection():
    try:
        requests.get("https://www.google.com/", timeout=5)
        return True
    except requests.ConnectionError:
        return False    
def check_connection():
    if internet_connection():
        print("The Internet is connected.")

    else:
        print("The Internet is not connected.")
        sleep(5)
        exit(1)

