import json
import requests
import datetime
import sys


def show_contri(user):
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))

    link = "https://api.github.com/users/" + str(user) + "/events"

    response = requests.get(link)
    events = response.json()
    latest = []

    for event in events:
        if event["created_at"].startswith(today):
            latest.append(event)
    
    return (user + " have made " + str(len(latest)) + " contributions today.")


def run():
	if len(sys.argv) > 1:
		print(show_contri(sys.argv[1]))
	else:
		print("Enter a valid username to stalk. \nFor eg: stalk aashutoshrathi")

if __name__ == '__main__':
	run()