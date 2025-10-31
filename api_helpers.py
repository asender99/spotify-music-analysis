from authenticator import Authenticator
import requests

class api_requestor():
    def __init__(self, authenticator: Authenticator):
        self.authenticator = authenticator

    def get_request(self, endpoint: str, params: dict = None) -> dict:
        headers = { 
            'Authorization': f'{self.authenticator.bearer_token} {self.authenticator.access_token}',
            'Content-Type': 'application/json'  # Example: if sending JSON data
        }
        api_url = f'https://api.spotify.com/v1/{endpoint}'
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            # Process the response
            print("Request successful!")
            print("Response status code:", response.status_code)
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")