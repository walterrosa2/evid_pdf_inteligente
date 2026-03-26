import requests

def test_login():
    url = "http://localhost:8003/token"
    payload = {"username": "admin", "password": "admin"}
    try:
        resp = requests.post(url, data=payload)
        print(f"Status Code: {resp.status_code}")
        print(f"Response Body: {resp.text}")
    except Exception as e:
        print(f"Error connecting to backend: {e}")

if __name__ == "__main__":
    test_login()
