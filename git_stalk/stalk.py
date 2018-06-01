import json
import requests
import datetime
import sys
import re
import datetime
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
    # print(tukde[len(tukde)-2])
    if tukde[len(tukde)-2] == user:  
        response = requests.get(link)
        repo = response.json()
        # print(repo["fork"])
        if not repo["fork"]:
            return True
        return False
    return True


def get_time(string):
    dt = string.split('T')
    # date = dt[0]
    time = dt[1][:-1]
    return(time)


def show_contri(user):
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    # today = "2018-05-31"
    link = "https://api.github.com/users/" + str(user) + "/events"
    user_link = "https://api.github.com/users/" + str(user)

    user_profile = requests.get(user_link)
    profile = user_profile.json()

    print("Name:", profile["name"])
    print("Company:", profile["company"])
    print("Followers:", profile["followers"])
    print("Following:", profile["following"])
    print("Public Repos:", profile["public_repos"])
    print("Contributions Today: ")

    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    if response.status_code == 200:    
        for event in events:
            if event["created_at"].startswith(today) and event["type"] != "IssueCommentEvent":
                if event["type"] == "WatchEvent":
                    stars.append(event)
                elif check_for_fork(event["repo"]["url"], user):
                    latest.append(event)
    
    if latest:
        table = PrettyTable(["Type", "Repository", "Details"])
        for event in latest:
            table.add_row([get_event(event["type"]), event["repo"]["name"], get_details(event)])
        print(table)
    print(user + " have made " + str(len(latest)) + " public contribution(s) today.\n")
    
    print("Starred today: ")
    if stars:
        star_table = PrettyTable(["Repository", "Language"])
        for event in stars:
            star_table.add_row([event["repo"]["name"], get_details(event)])
        print(star_table)
    return (user + " have starred " + str(len(stars)) + " repo(s) today.")


def run():
	if len(sys.argv) > 1:
		print(show_contri(sys.argv[1]))
	else:
		print("Enter a valid username to stalk. \nFor eg: stalk aashutoshrathi")

if __name__ == '__main__':
	run()