import os
import requests


backend_url = os.getenv('BACKEND_URL', "http://localhost:5000")

def fetch_streams():
    url = backend_url + '/streams'
    res = requests.get(url).json()
    return res
