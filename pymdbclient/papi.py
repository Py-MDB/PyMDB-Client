"""
PyMDB - Python CMDB

This file is part of the PyMDB project and is licensed under the Mozilla Public License, version 2.0 (MPL-2.0).

You may obtain a copy of the MPL-2.0 at:
https://mozilla.org/MPL/2.0/

Under the terms of this license, you are free to use, modify, and distribute this file, provided that any modifications
you make are also licensed under the MPL-2.0. For full terms and conditions, refer to the license linked above.

Author(s): Jesse Butryn (jesse@jesseb.org)
"""


import requests
import json
from pymdbclient.config import ConfigReader
import argparse


class Papi:
    def __init__(self, base_url, user_token, app_token):
        """
        Initialize the HttpClient with a base URL.

        Args:
            base_url (str): The base URL of the REST API.
        """
        self.base_url = base_url
        self.user_token = user_token
        self.app_token = app_token
        self.headers = {
            'User-Token': self.user_token,
            'App-Token': self.app_token,
            "Content-Type": "application/json",
        }

    def _request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}/{endpoint}"
        headers = self.headers.copy()
        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data)
        response = requests.request(method, url, params=params, data=data, headers=headers)
        try: 
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}\n{response.text}")
        return response

    def get(self, endpoint, params=None):
        """
        Send a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict): The query parameters to include in the request.

        Returns:
            Response: The response from the API.
        """
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint, data=None, params=None):
        """
        Send a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The form data to include in the request.

        Returns:
            Response: The response from the API.
        """
        return self._request("POST", endpoint, data=data, params=params)

    def put(self, endpoint, data=None, params=None):
        """
        Send a PUT request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The form data to include in the request.

        Returns:
            Response: The response from the API.
        """
        return self._request("PUT", endpoint, data=data, params=params)

    def delete(self, endpoint, data=None, params=None):
        """
        Send a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict): The query parameters to include in the request.

        Returns:
            Response: The response from the API.
        """
        return self._request("DELETE", endpoint, data=data, params=params)

    def paginate(self, endpoint, params=None):
        """
        Paginate through all pages of the endpoint and combine results.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict): The query parameters to include in the request.

        Returns:
            Response: The response object with combined results and other attributes.
        """
        if params is None:
            params = {}
        elif not isinstance(params, dict):
            raise TypeError("params must be a dictionary")
        
        combined_results = []
        while True:
            response = self._request("GET", endpoint, params=params)
            response_json = response.json()
            top_level_key = next(iter(response_json.keys() - {'meta'}))
            combined_results.extend(response_json.get(top_level_key, []))
            meta = response_json.get('meta', {})
            next_page_url = meta.get('next_page_url')
            if not next_page_url:
                break
            params = {**params, 'page': meta['page'] + 1}

        response._content = bytes(json.dumps(combined_results), 'utf-8')
        return response


def main():
    parser = argparse.ArgumentParser(description='papi - execute an API request against the PyMDB API')

    parser.add_argument('-e', '--endpoint', type=str, required=True, help='URL endpoint to execute against.')
    parser.add_argument('-m', '--params', type=str, help="Optional parameters for the request")
    parser.add_argument('-d', '--data', type=str, help="Optional JSON data for the request.")

    action_group = parser.add_mutually_exclusive_group(required=False)
    action_group.add_argument('-g', '--get', action="store_true", help="Execute a GET request.  (default)")
    action_group.add_argument('-D', '--delete', action="store_true", help="Execute a DELETE request.")
    action_group.add_argument('-p', '--put', action="store_true", help="Execute a PUT request.")
    action_group.add_argument('-P', '--post', action="store_true", help="Execute a POST request.")
    action_group.add_argument('-r', '--paginate', action="store_true", help="Paginate through all pages of the endpoint.")

    args = parser.parse_args()

    configreader = ConfigReader()
    base_url = configreader.get_base_url()
    user_token = configreader.get_user_token()
    app_token = configreader.get_app_token()

    papi = Papi(base_url, user_token, app_token)

    endpoint = args.endpoint
    params = args.params
    data = args.data
    
    if args.delete:
        result = papi.delete(endpoint, data, params)
    elif args.put:
        result = papi.put(endpoint, data, params)
    elif args.post:
        result = papi.post(endpoint, data, params)
    elif args.paginate:
        result = papi.paginate(endpoint, params)
    else:
        result = papi.get(endpoint, params)

    try:
        result.raise_for_status()
        json_out = json.dumps(result.json())
        print(json_out)
    except requests.exceptions.HTTPError as err:
        print(f"Error: {err}, Status Code: {result.status_code}")

if __name__ == "__main__":
    main()
