import json
import requests
import config.config as config


with open(config.KEY, encoding='utf-8') as file:
    api_key = json.load(file)['Authorization']

print(api_key)


# TODO create function for getting the responses, and then
#  few functions to test requests response codes.