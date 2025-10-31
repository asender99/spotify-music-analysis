import logging
import json
from pathlib import Path    
import os
import requests
from datetime import datetime, timedelta

class Authenticator():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._client_token_path = Path('data') / 'tokens' /  'spotify_token.json'
        self.client_access_token_path = Path('data') / 'tokens' / 'spotify_access_token.json'
        self._token_info: dict  

        self._access_token: str = ""
        self._bearer_token: str = ""

        self.auth_flow()

    @property
    def access_token(self) -> str:
        if self._check_access_token_validity():
            return self._access_token
        else:
            self.auth_flow()
            return self._access_token
    
    @access_token.setter
    def access_token(self, token: str):
        self._access_token = token

    @property
    def bearer_token(self) -> str:
        if self._check_access_token_validity():
            return self._bearer_token
        else:
            self.auth_flow()
            return self._bearer_token

    @bearer_token.setter
    def bearer_token(self, token: str):
        self._bearer_token = token

    def _get_authentication_token(self):
        self.logger.info("Retrieving authentication token")
        with open(self._client_token_path, 'r') as f:
            self._token_info = json.load(f)

    def _authenticate(self):
        self.logger.info("Authenticating with Spotify API")
        self._get_authentication_token()
        current_time = datetime.now()
        auth_response = requests.post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'client_credentials',
            'client_id': self._token_info['client_id'],
            'client_secret': self._token_info['client_secret'],
        })
        if auth_response.status_code != 200:
            self.logger.error("Failed to authenticate with Spotify API")
            raise Exception("Authentication failed")
        auth_data = auth_response.json()
        expiry_time = current_time + timedelta(seconds=auth_data['expires_in'])
        auth_data['expiry_time'] = expiry_time.isoformat()
        self.logger.debug("Authentication successful")
        return auth_data
    
    def _check_access_token_validity(self) -> bool:
        self.logger.info("Checking access token validity")
        if not os.path.exists(self.client_access_token_path):
            self.client_access_token_path.touch()
            return False
        with open(self.client_access_token_path, 'r') as f:
            try:
                token_data = json.load(f)
            except json.JSONDecodeError:
                print("Access token file is empty or corrupted")
                self.logger.debug("Access token file is empty or corrupted")
                return False
            expiry_time = datetime.fromisoformat(token_data['expiry_time'])
            if datetime.now() < expiry_time:
                self.logger.debug("Access token is valid")
                return True
            else:
                self.logger.debug("Access token has expired")
                return False
    
    def save_access_token(self, access_info: dict):
        self.logger.info("Saving access token")
        with open(self.client_access_token_path, 'r+') as f:
            f.seek(0)
            json.dump(access_info, f, indent=4)
            f.truncate()
        self.access_token = access_info['access_token']
        self.bearer_token = access_info['token_type']
        self.logger.info("Access token saved successfully")

    def _set_vars_from_saved_token(self):
        self.logger.info("Setting variables from saved token")
        with open(self.client_access_token_path, 'r') as f:
            token_data = json.load(f)
            self.access_token = token_data['access_token']
            self.bearer_token = token_data['token_type']
        self.logger.info("Variables set successfully")

    def auth_flow(self):
        self.logger.info("Starting authentication flow")
        if self._check_access_token_validity():
            self.logger.info("Access token is already valid, skipping authentication")
            self._set_vars_from_saved_token()
            return
        token = self._authenticate()
        self.save_access_token(token)
        self.logger.info("Authentication flow completed")