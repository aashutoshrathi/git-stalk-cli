import json
import requests
import datetime
import sys
import re
import datetime
from dateutil import tz
from prettytable import PrettyTable

def jft(user):
    user_link = "https://api.github.com/users/" + str(user)
    response = requests.get(user_link)
    return response.status_code

def get_event(string):
    event = ""
    words = re.findall('[A-Z][^A-Z]*', string)
    for word in words:
        event += word
        event += " "
    if event == "Pull Request Review Comment Event ":
        event = "PR Review Event "
    if event == "Watch Event ":
        event = "Starred Event "
    if event == "Create Event ":
        event = "Commit Event "
    return event[:-7]


def get_details(event):
    if event["type"] == "IssuesEvent":
        return event["payload"]["issue"]["title"]
    if event["type"] == "IssueCommentEvent":
        return event["payload"]["comment"]["body"]
    if event["type"] == "WatchEvent":
        response = requests.get(event["repo"]["url"])
        repo = response.json()
        return repo["language"]
    if event["type"] == "PullRequestEvent":
        return event["payload"]["pull_request"]["title"]
    if event["type"] == "PushEvent":
        for commit in event["payload"]["commits"]:
            if commit["distinct"]:
                return commit["message"]

def check_for_fork(link, user):
    tukde = link.split('/')
    if tukde[len(tukde)-2] == user:  
        response = requests.get(link)
        repo = response.json()
        if not repo["fork"]:
            return True
        return False
    return True


def get_local_time(string):
    local_time = convert_to_local(string)
    tukde = local_time.split(' ')
    samay = tukde[1].split('+')[0]
    return samay

def get_basic_info(profile):
    print("Name:", profile["name"])
    print("Company:", profile["company"])
    print("Followers:", profile["followers"])
    print("Following:", profile["following"])
    print("Public Repos:", profile["public_repos"])
    print("Contributions Today: ")


def convert_to_local(string):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_stamp = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=from_zone)
    local_stamp = utc_stamp.astimezone(to_zone)
    return(str(local_stamp))


def show_contri(user):
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    # today = "2018-06-02"
    link = "https://api.github.com/users/" + str(user) + "/events"
    user_link = "https://api.github.com/users/" + str(user)

    user_profile = requests.get(user_link)
    profile = user_profile.json()

    get_basic_info(profile)

    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    if response.status_code == 200:    
        for event in events:
            if convert_to_local(event["created_at"]).startswith(today) and event["type"] != "IssueCommentEvent":
                if event["type"] == "WatchEvent":
                    stars.append(event)
                elif check_for_fork(event["repo"]["url"], user):
                    latest.append(event)
    
    if latest:
        table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in latest:
            table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(event["created_at"]), get_details(event)])
        print(table)
    print(user + " have made " + str(len(latest)) + " public contribution(s) today.\n")
    
    print("Starred today: ")
    if stars:
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for event in stars:
            star_table.add_row([event["repo"]["name"], get_details(event), get_local_time(event["created_at"])])
        print(star_table)
    return (user + " have starred " + str(len(stars)) + " repo(s) today.")


def run():
	if len(sys.argv) > 1:
		print(show_contri(sys.argv[1]))
	else:
		print("Enter a valid username to stalk. \nFor eg: stalk aashutoshrathi")

if __name__ == '__main__':
	run()