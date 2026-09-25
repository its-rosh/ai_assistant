import requests


BASE_URL = "http://127.0.0.1:5000"

session = requests.Session()

# Login
login_response = session.post(
    f"{BASE_URL}/api/login",
    json={
        "email": "test@example.com",
        "password": "TestPassword123!",
    },
)

print("LOGIN:")
print(login_response.status_code)
print(login_response.json())

# Check authenticated user
me_response = session.get(f"{BASE_URL}/api/me")

print("\nCURRENT USER:")
print(me_response.status_code)
print(me_response.json())