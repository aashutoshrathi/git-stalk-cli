import requests
import datetime
import re
import os
import argparse
from collections import namedtuple
from dateutil import tz
from prettytable import PrettyTable

github_uri = "https://api.github.com/users/"
StarredRepo = namedtuple('StarredRepo', ['name', 'language', 'time'])

def jft(user):
    user_link = "{}{}".format(github_uri, str(user))
    response = requests.get(user_link)
    return response.status_code


def get_event(string):
    """Returns the event"""
    event = ""
    words = re.findall('[A-Z][^A-Z]*', string)
    event = " ".join(words)
    if event == "Pull Request Review Comment Event":
        event = "PR Review Event"
    if event == "Watch Event":
        event = "Starred Event"
    if event == "Create Event":
        event = "Commit Event"
    return event[:-6]


def get_details(event):
    """Returns the details of the event according to the type of the event"""
    if event["type"] == "IssuesEvent":
        return event["payload"]["issue"]["title"]
    elif event["type"] == "IssueCommentEvent":
        return event["payload"]["comment"]["body"]
    elif event["type"] == "PullRequestEvent":
        return event["payload"]["pull_request"]["title"]
    elif event["type"] == "PushEvent":
        for commit in event["payload"]["commits"]:
            if commit["distinct"]:
                return commit["message"]
    elif event["type"] == "MemberEvent":
        return "Added {} as collaborator".format(
            event["payload"]["member"]["login"]
        )
    elif event["type"] == "ReleaseEvent":
        return "Released binaries for version {}".format(
            event["payload"]["release"]["tag_name"]
        )
    elif event["type"] == "ForkEvent":
        return "Forked " + event["repo"]["name"]


def check_for_fork(link, user):
    """Check wheather it is a forked"""
    tukde = link.split('/')
    if tukde[len(tukde) - 2] == user:
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
    user_link = "{}{}".format(github_uri, str(user))
    user_profile = requests.get(user_link)
    profile = user_profile.json()
    print("Name:", profile["name"])
    print("Company:", profile["company"])
    print("Bio:", profile["bio"])
    print("Followers:", profile["followers"])
    print("Following:", profile["following"])
    print("Public Repos:", profile["public_repos"])
    print ("Public Gists:",profile["public_gists"])
    print("Open for hiring:",profile["hireable"])
    print()


def convert_to_local(string):
    """Returns the local_stamp as string"""
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_stamp = datetime.datetime.strptime(
        string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=from_zone)
    local_stamp = utc_stamp.astimezone(to_zone)
    return(str(local_stamp))

def date_time_validate(date_text):
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def get_contributions(user, latest, org=None, flag=False):
    """
        Traverses the latest array,
        creates a table
        if org argument is present only the repos which belong to the org is added to the table
        and prints the table.
    """
    print("Contributions Today: ")
    if latest:
        for event in latest:
            temp = {'type':get_event(event["type"]), 'repository':event["repo"]["name"], 'time':get_local_time(
                event["created_at"]), 'details':get_details(event)}
            info.append(temp)

    if flag:
        return info
    else:
        print("Contributions Today: ")
        table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for details in info:
            repo_name = details["repository"]
            if org:
                curr_org = ""
                for c in repo_name:
                    if c == r'/':
                        break
                    curr_org += c
                if curr_org == org:
                    table.add_row([details['type'], details['repository'], details['time'], details['details']])
            else:
                table.add_row([details['type'], details['repository'], details['time'], details['details']])
        print(table)
        print(user + " have made " + str(len(latest)) +
                      " public contribution(s) today.\n")


def get_other_activity(user, other, flag = False):
    """
        Traverses the other array,
        creates a table
        and prints the table.
    """
    info = []
    if other:
        for event in other:
            temp = {'type':get_event(event["type"]), 'repository':event["repo"]["name"], 'time':get_local_time(
                event["created_at"]), 'details':get_details(event)}
            info.append(temp)
    if flag:
        return info
    else:
        print("Other Activity today: ")
        other_table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for details in info:
            other_table.add_row([details['type'], details['repository'], details['time'], temp['details']])
        print(other_table)
        print(user + " have done " + str(len(other)) +
                  " other public activit(y/ies) today.\n")


def display_stars(user, stars, flag = False):
    """
        Traverses the stars array,
        creates a table
        and prints the table.
    """
    info = []
    if stars:
        for event in stars:
            temp = {'repository':event["repo"]["name"], 'language':get_details(
                event), 'time': get_local_time(event["created_at"])}
            info.append(temp)

    if flag:
        return info
    else:
        print("Starred today:")
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for details in info:
            star_table.add_row([details['repository'], details['language'], details['time']])
        print(star_table)
        print(user + " have starred " + str(len(stars)) + " repo(s) today.")


def fill_todays_data_data(user, events, latest, stars, other):
    """Traverses the events array and seperates individual data to latest, stars and other arrays"""
    for event in events:
        event_type_issue_comment_event = event["type"] != "IssueCommentEvent"

        if event_type_issue_comment_event:
            if event["type"] == "WatchEvent":
                stars.append(event)
            elif event["type"] in ("ForkEvent", "MemberEvent"):
                other.append(event)
            elif check_for_fork(event["repo"]["url"], user):
                latest.append(event)
    return latest, stars, other

  
def get_language_for_repo(url):
    response = requests.get(url)
    repo = response.json()
    return repo['language']

  
def create_star(event):
    language = get_language_for_repo(event['repo']['url'])
    return StarredRepo(name=event['repo']['name'], language=language, time=get_local_time(event['created_at']))


def update():
    """Runs the upgrade command and upgrades git-stalk"""
    os.system("pip install --upgrade git-stalk")


def filter_since_until_dates(events, since_date=None, until_date=None):
    """Filters the events based on since and until dates"""
    filtered_events = []
    if since_date and until_date:
        for e in events:
            created_at = datetime.datetime.strptime(e['created_at'][:10], "%Y-%m-%d")
            if created_at >= since_date and created_at <= until_date:
                filtered_events.append(e)
    elif since_date:
        for e in events:
            created_at = datetime.datetime.strptime(e['created_at'][:10], "%Y-%m-%d")
            if created_at >= since_date:
                filtered_events.append(e)
            else:
                break
    elif until_date:
        for e in events:
            created_at = datetime.datetime.strptime(e['created_at'][:10], "%Y-%m-%d")
            if created_at <= until_date:
                filtered_events.append(e)
    return filtered_events

def getipaddress(args=None):
    return (requests.get("http://ipecho.net/plain?").text)
  
def show_contri(args=None):
    """Sends a get request to github rest api and display data using the utility functions"""
    user = args["name"]
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    link = "{}{}/events".format(github_uri, str(user))
    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    other = []
    if response.status_code == 200:
        if args["since"] and args["until"]:
            since_date = datetime.datetime.strptime(args["since"], "%m-%d-%Y")
            until_date = datetime.datetime.strptime(args["until"], "%m-%d-%Y")
            events = filter_since_until_dates(events, since_date=since_date, until_date=until_date)
        elif args["since"]:
            since_date = datetime.datetime.strptime(args["since"], "%m-%d-%Y")
            events = filter_since_until_dates(events, since_date=since_date)
        elif args["until"]:
            until_date = datetime.datetime.strptime(args["until"], "%m-%d-%Y")
            events = filter_since_until_dates(events, until_date=until_date)
        if response.status_code == 200:
            if 'since_date' in vars() or 'until_date' in vars():
                latest, stars, other = fill_dated_data(
                user, events, latest, stars, other)
            else:
                latest, stars, other = fill_todays_data(
                    user, today, events, latest, stars, other)
    elif response.status_code == 404:
        print(
            "User with username {0} does not exists, please check and try again"
            .format(str(user))
        )
        return
    elif response.status_code == 403:
        print(
            "API rate limit exceeded for ip address ,"+getipaddress()+" try again later or change ip adress."
        )

    else:
        print(
            "Something went wrong, please check your internet connection \n"
            "Use stalk --help for Help"
        )
        return

    if args["np"] is False:
        get_basic_info(user)

    if args["org"]:
        get_contributions(user, latest, args["org"])
    else:
        get_contributions(user, latest)

    get_other_activity(user, other)
    display_stars(user, stars)


def run():
    """Parsing the command line arguments using argparse and calls the update or show_contri function as required"""
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs='?', help="name of the user")
    ap.add_argument("--org", help="Organization Name")
    ap.add_argument(
        "-U", "--update",
        action='store_true',
        help=(
            "Update this program to latest version. Make sure that you have"
            " sufficient permissions (run with sudo if needed)"
        )
    )
    ap.add_argument("-np", action='store_true',
                    help="Stalks a user without showing their profile")
    ap.add_argument("--since", help="Take into account only events since date. Date format MM-DD-YYYY")
    ap.add_argument("--until", help="Take into account only events after date. Date format MM-DD-YYYY")
    args = vars(ap.parse_args())

    if len(args) > 1:
        if args["update"]:
            update()
        # elif(sys.argv[1] == "--version"):
        #     show_version()
        else:
            show_contri(args)
    else:
        print(
            "Enter a valid username to stalk. \n"
            "For eg: stalk aashutoshrathi \n"
            "Or you can type stalk --help for help"
        )


if __name__ == '__main__':
    run()
