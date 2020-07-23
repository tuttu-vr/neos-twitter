import argparse
from urllib.parse import unquote
import requests

parser = argparse.ArgumentParser()
parser.add_argument('token')
parser.add_argument('count', default=3, type=int)
args = parser.parse_args()

res = requests.get('http://localhost:8080/recent', {
    'key': args.token,
    'count': args.count
})

print(res.text)

data = res.text.split('|')
datetime_str = data[0]
num_of_messages = data[1]
messages = data[2].split('$')

for message in messages:
    message_data = message.split(';')

    name = unquote(message_data[0])
    icon_url = unquote(message_data[1])
    images = list(map(unquote, message_data[2].split(',')))
    image_url = unquote(message_data[3])
    text = unquote(message_data[4])

    print(name, icon_url, image_url, images, text)
