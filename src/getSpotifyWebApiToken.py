import requests
import base64
import os
from dotenv import load_dotenv
load_dotenv()

client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
encoded = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")

headers = {
     "Content-Type": "application/x-www-form-urlencoded",
     "Authorization": "Basic " + encoded
} 
payload = {
     "grant_type": "client_credentials"
} 
response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)

print(response)
print(response.text)