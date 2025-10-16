import requests

API_URL = 'https://smmpakpanel.com/api/v2'  
API_KEY = 'e89f3cfcaa4a648a8f8e5e63912dc987'

def add_order(service_id, link, quantity):
    data = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    response = requests.post(API_URL, data=data)
    return response.json()

def get_refill_status(refills):
    data = {
        'key': API_KEY,
        'action': 'refill_status',
        'refills': refills
    }
    response = requests.post(API_URL, data=data)
    return response.json()

def create_cancel(orders):
    data = {
        'key': API_KEY,
        'action': 'cancel',
        'orders': orders
    }
    response = requests.post(API_URL, data=data)
    return response.json()

def get_balance():
    data = {
        'key': API_KEY,
        'action': 'balance'
    }
    response = requests.post(API_URL, data=data)
    return response.json()