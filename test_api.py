# calls an http API
# the api is at http://localhost:8080/api

import requests

def call_api():
    url = 'http://localhost:8080/api/' 
    try:
        username = 'manel'
        password = 'ThisIsAPassword'

        body = {
            "usernameOrEmail": username,
            "password": password
        }
        response = requests.get(url, json=body)
        if response.status_code == 200:
            print("Request successfull:", response.text)
        else:
            print("Request unsuccessfull:", response.status_code)
            print(response.text)
    except requests.RequestException as e:
        print("Error:", e)
