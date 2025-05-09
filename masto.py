#!/usr/bin/python3
from mastodon import Mastodon

instance_url = "https://fsebugoutzone.org"

with open('client.secret', 'r') as clients:
    clients = clients.read()
if len(clients) < 5:
    Mastodon.create_app(
        'myapp',
        api_base_url = instance_url,
        to_file = "client.secret"
    )

# read login file
with open('login', 'r') as login_file:
    login_data = login_file.readlines()
    username = login_data[0].split('=')[1].strip()
    password = login_data[1].split('=')[1].strip()

mastodon = Mastodon(
    client_id = "client.secret",
    api_base_url = instance_url
)

mastodon.log_in(
    username,
    password,
    to_file="user.secret"
)

mastodon = Mastodon(
    client_id = "client.secret",
    access_token = "user.secret",
    api_base_url = instance_url
)

#mastodon.toot("Connected")