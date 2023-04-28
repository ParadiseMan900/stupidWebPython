import requests
r = requests.get('http://localhost:1234/')
print(r.status_code)
print(r.text)