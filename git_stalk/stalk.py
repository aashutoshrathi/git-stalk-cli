import json
import requests
import datetime
import sys
import re
import os
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
    elif event["type"] == "IssueCommentEvent":
        return event["payload"]["comment"]["body"]
    elif event["type"] == "WatchEvent":
        response = requests.get(event["repo"]["url"])
        repo = response.json()
        return repo["language"]
    elif event["type"] == "PullRequestEvent":
        return event["payload"]["pull_request"]["title"]
    elif event["type"] == "PushEvent":
        for commit in event["payload"]["commits"]:
            if commit["distinct"]:
                return commit["message"]
    elif event["type"] == "MemberEvent":
        return "Added " + event["payload"]["member"]["login"] + " as collaborator"
    elif event["type"] == "ReleaseEvent":
        return "Released binaries for version " + event["payload"]["release"]["tag_name"]
    elif event["type"] == "ForkEvent":
        return "Forked " + event["repo"]["name"]

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

def get_basic_info(user):
    user_link = "https://api.github.com/users/" + str(user)
    user_profile = requests.get(user_link)
    profile = user_profile.json()
    print("Name:", profile["name"])
    print("Company:", profile["company"])
    print("Bio:", profile["bio"])
    print("Followers:", profile["followers"])
    print("Following:", profile["following"])
    print("Public Repos:", profile["public_repos"])
    print()


def convert_to_local(string):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_stamp = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=from_zone)
    local_stamp = utc_stamp.astimezone(to_zone)
    return(str(local_stamp))


def get_contributions(user, latest):
    print("Contributions Today: ")
    if latest:
        table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in latest:
            table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(event["created_at"]), get_details(event)])
        print(table)
    print(user + " have made " + str(len(latest)) + " public contribution(s) today.\n")


def get_other_activity(user, other):
    print("Other Activity today: ")
    if other:
        other_table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in other:
            other_table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(event["created_at"]), get_details(event)])
        print(other_table)
    print(user + " have done " + str(len(other)) + " other public activit(y/ies) today.\n")


def get_stars(user, stars):
    print("Starred today: ")
    if stars:
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for event in stars:
            star_table.add_row([event["repo"]["name"], get_details(event), get_local_time(event["created_at"])])
        print(star_table)
    print (user + " have starred " + str(len(stars)) + " repo(s) today.")


def fill_data(user, today, events, latest, stars, other):
    for event in events:
        if convert_to_local(event["created_at"]).startswith(today) and event["type"] != "IssueCommentEvent":
            if event["type"] == "WatchEvent":
                stars.append(event)
            elif event["type"] == "ForkEvent" or event["type"] == "MemberEvent":
                other.append(event)
            elif check_for_fork(event["repo"]["url"], user):
                latest.append(event)
    return latest, stars, other


def update():
    os.system("pip install --upgrade git-stalk")

def show_help():
    print("Usage: stalk [OPTIONS] username [USERNAME]")
    print("Options:\n  General Options:")
    print("    -h, --help                       Print this help text and exit")
    # print("    --version                        Print program version and exit")
    print("    -np                              Stalks a user without showing their profile")
    print("    -U, --update                     Update this program to latest version. Make sure that you have sufficient permissions (run with sudo if needed)")


def show_contri(user, arg=None):
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    link = "https://api.github.com/users/" + str(user) + "/events"    
    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    other = []
    if response.status_code == 200:    
        latest, stars, other = fill_data(user, today, events, latest, stars, other)
    else:
        print("Something went wrong, check your internet or username. \nUse stalk --help for Help")
        return
    
    if arg != "-np":
        get_basic_info(user)

    get_contributions(user, latest)
    get_other_activity(user, other)
    get_stars(user, stars)


def run():
    if len(sys.argv) > 1:
        if(sys.argv[1] == "--help" or sys.argv[1] == "-h"):
            show_help()
        elif(sys.argv[1] == "--update" or sys.argv[1] == "-U"):
            update()
        # elif(sys.argv[1] == "--version"):
        #     show_version()
        elif len(sys.argv) == 3:
            show_contri(sys.argv[2], (sys.argv[1]))
        elif len(sys.argv) == 2:
            show_contri(sys.argv[1])
    else:
        print("Enter a valid username to stalk. \nFor eg: stalk aashutoshrathi \nOr you can type stalk --help for help")

if __name__ == '__main__':
	run()