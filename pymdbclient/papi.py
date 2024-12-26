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
    def __init__(self, base_url):
        """
        Initialize the HttpClient with a base URL.

        Args:
            base_url (str): The base URL of the REST API.
        """
        self.base_url = base_url

    def get(self, endpoint, params=None):
        """
        Send a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict): The query parameters to include in the request.

        Returns:
            Response: The response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response

    def post(self, endpoint, data=None, json=None):
        """
        Send a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The form data to include in the request.
            json (dict): The JSON data to include in the request.

        Returns:
            Response: The response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, data=data, json=json)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response

    def put(self, endpoint, data=None, json=None):
        """
        Send a PUT request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            data (dict): The form data to include in the request.
            json (dict): The JSON data to include in the request.

        Returns:
            Response: The response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, data=data, json=json)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response

    def delete(self, endpoint, params=None):
        """
        Send a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to send the request to.
            params (dict): The query parameters to include in the request.

        Returns:
            Response: The response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response

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
            response = self.get(endpoint, params=params)
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
    papi = Papi(base_url)

    endpoint = args.endpoint
    params = args.params
    data = args.data
    
    if args.delete:
        result = papi.delete(endpoint, params)
    elif args.put:
        result = papi.put(endpoint, params)
    elif args.post:
        result = papi.post(endpoint, params)
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
