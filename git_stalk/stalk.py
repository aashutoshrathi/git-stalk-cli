import json
import requests
import datetime
import sys
import re
import os
import datetime
import argparse
from dateutil import tz
from prettytable import PrettyTable


def jft(user):
    user_link = "https://api.github.com/users/" + str(user)
    response = requests.get(user_link)
    return response.status_code


def get_event(string):
    """Returns the event"""
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
    """Returns the details of the event according to the type of the event"""
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
    """Check wheather it is a forked"""
    tukde = link.split('/')
    if tukde[len(tukde)-2] == user:
        response = requests.get(link)
        repo = response.json()
        if not repo["fork"]:
            return True
        return False
    return True


def get_local_time(string):
    """Returns the local time"""
    local_time = convert_to_local(string)
    tukde = local_time.split(' ')
    samay = tukde[1].split('+')[0]
    return samay


def get_basic_info(user):
    """Prints the user's basic info"""
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
    """Returns the local_stamp as string"""
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_stamp = datetime.datetime.strptime(
        string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=from_zone)
    local_stamp = utc_stamp.astimezone(to_zone)
    return(str(local_stamp))


def get_contributions(user, latest, org=None):
    """
        Traverses the latest array,
        creates a table
        if org argument is present only the repos which belong to the org is added to the table
        and prints the table.
    """
    print("Contributions Today: ")
    if latest:
        table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in latest:
            repo_name = event["repo"]["name"]
            if org:
                curr_org = ""
                for c in repo_name:
                    if c == r'/':
                        break
                    curr_org += c
                if curr_org == org:
                    table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(
                        event["created_at"]), get_details(event)])
            else:
                table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(
                    event["created_at"]), get_details(event)])
        print(table)
    print(user + " have made " + str(len(latest)) +
          " public contribution(s) today.\n")


def get_other_activity(user, other):
    """
        Traverses the other array,   
        creates a table
        and prints the table.
    """
    print("Other Activity today: ")
    if other:
        other_table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in other:
            other_table.add_row([get_event(event["type"]), event["repo"]["name"], get_local_time(
                event["created_at"]), get_details(event)])
        print(other_table)
    print(user + " have done " + str(len(other)) +
          " other public activit(y/ies) today.\n")


def get_stars(user, stars):
    """
        Traverses the stars array,
        creates a table
        and prints the table.
    """
    print("Starred today: ")
    if stars:
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for event in stars:
            star_table.add_row([event["repo"]["name"], get_details(
                event), get_local_time(event["created_at"])])
        print(star_table)
    print(user + " have starred " + str(len(stars)) + " repo(s) today.")


def fill_data(user, today, events, latest, stars, other):
    """Traverses the events array and seperates individual data to latest, stars and other arrays"""
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
    """Runs the upgrade command and upgrades git-stalk"""
    os.system("pip install --upgrade git-stalk")


def show_contri(args=None):
    """Sends a get request to github rest api and display data using the utility functions"""
    user = args["name"]
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    link = "https://api.github.com/users/" + str(user) + "/events"
    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    other = []
    if response.status_code == 200:
        latest, stars, other = fill_data(
            user, today, events, latest, stars, other)
    else:
        print("Something went wrong, check your internet or username. \nUse stalk --help for Help")
        return

    if args["np"] == False:
        get_basic_info(user)

    if args["org"]:
        get_contributions(user, latest, args["org"])
    else:
        get_contributions(user, latest)

    get_other_activity(user, other)
    get_stars(user, stars)


def run():
    """Parsing the command line arguments using argparse and calls the update or show_contri function as required"""
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs='?', help="name of the user")
    ap.add_argument("--org", help="Organization Name")
    ap.add_argument(
        "-U", "--update", action='store_true', help="Update this program to latest version. Make sure that you have sufficient permissions (run with sudo if needed)")
    ap.add_argument("-np", action='store_true',
                    help="Stalks a user without showing their profile")
    args = vars(ap.parse_args())

    if len(args) > 1:
        if args["update"]:
            update()
        # elif(sys.argv[1] == "--version"):
        #     show_version()
        else:
            show_contri(args)
    else:
        print("Enter a valid username to stalk. \nFor eg: stalk aashutoshrathi \nOr you can type stalk --help for help")


if __name__ == '__main__':
    run()
    
    