import requests
import os
from termcolor import colored
import json
import concurrent.futures


class Credentials:
    client_id = ''
    client_secret = ''
    access_token = ''
    headers = {}


def file_read(file_name:str):
  with open(file_name, "r") as raid_list:
      username_list = sorted(raid_list.read().splitlines())
  raid_list.close()

  url_list = []
  for i in range(0, len(username_list)):
    url_list.append('https://api.twitch.tv/helix/streams?user_login=' + username_list[i])

  return [username_list, url_list]


def generate_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    myobj = {'client_id': Credentials.client_id,
            'client_secret': Credentials.client_secret,
            'grant_type' : 'client_credentials'}

    response = requests.post(url, json = myobj).json()
    return response['access_token']

def send_get_request(url, headers):
    # 
    response = requests.get(url, headers=headers)
    # responses.append(requests.get(url, headers=headers))
    return response


f = open("credentials.json")
data = json.load(f)
Credentials.client_id = data['client_id']
Credentials.client_secret = data['client_secret']
Credentials.access_token = data['access_token']
f.close()

Credentials.headers = {'Client-ID': Credentials.client_id,
        'Authorization': 'Bearer ' + Credentials.access_token}

response = requests.get('https://api.twitch.tv/helix/streams?user_login=', headers = Credentials.headers).json()

if(response['status'] == 401):
    token = generate_access_token()
    f = open("credentials.json")
    data = json.load(f)
    data['access_token'] = token
    Credentials.access_token = token
    f = open("credentials.json", "w")
    json.dump(data, f)
    f.close()

Credentials.headers = {'Client-ID': Credentials.client_id,
        'Authorization': 'Bearer ' + Credentials.access_token}
        
os.system("color")
[username_list, url_list] = file_read("raid_list.txt")

ok = False
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = list()
    for url in url_list:
        futures.append(executor.submit(send_get_request, url=url, headers=Credentials.headers))
    for future in concurrent.futures.as_completed(futures):
        if future.result().status_code == 200:
            stream_data = future.result().json()
            if len(stream_data['data']) == 1:
                ok = True
                link = 'https://www.twitch.tv/' + stream_data['data'][0]['user_name']
                print('\n' + colored(stream_data['data'][0]['user_name'], 'yellow') + ' is playing ' + colored(stream_data['data'][0]['game_name'], 'yellow') + ': ' + stream_data['data'][0]['title'] + 
                    '\n' + colored(link, 'dark_grey'))


if(ok is False):
    print('There are no live users.')

ok = False

print('\n')
os.system("pause")