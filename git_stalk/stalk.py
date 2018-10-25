from __future__ import print_function
import argparse
import datetime
import os
import re
import sys
from collections import namedtuple
import requests
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
    types = {
        "IssuesEvent": event["payload"]["issue"]["title"],
        "IssuesCommentEvent": event["payload"]["comment"]["body"],
        "PullRequestEvent": event["payload"]["pull_request"]["title"],
        "PushEvent": "".join([commit["message"] for commit in event["payload"]["commits"] if commit["distinct"]]),
        "MemberEvent": "Added {} as collaborator".format(event["payload"]["member"]["login"]),
        "ReleaseEvent": "Released binaries for version {}".format(event["payload"]["release"]["tag_name"]),
        "ForkEvent": "Forked {}".format(event["repo"]["name"]),
    }
    return types.get(event["type"], "")


def check_for_fork(link, user):
    """Check whether it is a forked."""
    tukde = link.split('/')
    if tukde[len(tukde) - 2] == user:
        response = requests.get(link)
        repo = response.json()
        if not repo["fork"]:
            return True
        return False
    return True


def get_local_time(string):
    """Returns the local time."""
    local_time = convert_to_local(string)
    tukde = local_time.split(' ')
    samay = tukde[1].split('+')[0]
    return samay


def get_basic_info(user):
    """Prints the user's basic info."""

    user_link = "{}{}".format(github_uri, str(user))
    user_profile = requests.get(user_link)
    profile = user_profile.json()

    print("Name: {}".format(profile["name"]))
    print("Company: {}".format(profile["company"]))
    print("Bio: {}".format(profile["bio"]))
    print("Followers: {}".format(profile["followers"]))
    print("Following: {}".format(profile["following"]))
    print("Public Repos: {}".format(profile["public_repos"]))
    print("Public Gists: {}".format(profile["public_gists"]))
    print("Open for hiring: {} \n".format(profile["hireable"]))


def convert_to_local(string):
    """Returns the local_stamp as string."""

    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc_stamp = datetime.datetime.strptime(
        string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=from_zone)
    local_stamp = utc_stamp.astimezone(to_zone)
    return str(local_stamp)


def date_time_validate(date_text):
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def get_contributions(user, latest, date_text, org=None):
    """
        Traverses the latest array,
        creates a table
        if org argument is present only the repos which belong to the org \
        is added to the table
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
                    table.add_row([
                        get_event(event["type"]),
                        event["repo"]["name"],
                        get_local_time(event["created_at"]),
                        get_details(event)
                    ])
            else:
                table.add_row([
                    get_event(event["type"]),
                    event["repo"]["name"],
                    get_local_time(event["created_at"]),
                    get_details(event)
                ])
        print(table)
    print("{} have made {} public contribution(s) {}.\n".format(
        user, str(len(latest)), date_text))


def get_other_activity(user, other, date_text):
    """
        Traverses the other array,
        creates a table
        and prints the table.
    """
    print("Other Activity {}: ".format(date_text))
    if other:
        other_table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in other:
            other_table.add_row([
                get_event(event["type"]), event["repo"]["name"],
                get_local_time(event["created_at"]),
                get_details(event),
            ])
        print(other_table)
    print("{} have done {} other public activit(y/ies) {}.\n".format(
        user, str(len(other)), date_text))


def display_stars(user, stars, date_text):
    """
        Traverses the stars array,
        creates a table
        and prints the table.
    """
    print("Starred {}: ".format(date_text))
    if stars:
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for starred_repo in stars:
            star_table.add_row([
                starred_repo["repo"]["name"],
                get_language_for_repo(starred_repo["repo"]["url"]),
                get_local_time(starred_repo["created_at"])])
        print(star_table)
    print("{} have starred {} repo(s) {}.".format(
        user, str(len(stars)), date_text))


def fill_todays_data(user, today, events, latest, stars, other):
    """Traverses the events array and separates individual data to latest,
    stars and other arrays"""

    for event in events:
        starts_today = convert_to_local(event["created_at"]).startswith(today)
        event_type_issue_comment_event = event["type"] != "IssueCommentEvent"

        if starts_today and event_type_issue_comment_event:
            if event["type"] == "WatchEvent":
                stars.append(create_star(event))
            elif event["type"] in ("ForkEvent", "MemberEvent"):
                other.append(event)
            elif check_for_fork(event["repo"]["url"], user):
                latest.append(event)
    return latest, stars, other


def fill_dated_data(user, events, latest, stars, other):
    """Traverses the events array and seperates individual data to latest,
    stars and other arrays"""

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
    return StarredRepo(
        name=event['repo']['name'], language=language,
        time=get_local_time(event['created_at']))


def update():
    """Runs the upgrade command and upgrades git-stalk"""
    os.system("pip install --upgrade git-stalk")


def filter_since_until_dates(events, since_date=None, until_date=None):
    """Filters the events based on since and until dates"""
    event_tuples = [(datetime.datetime.strptime(event['created_at'][:10], "%Y-%m-%d"), event) for event in events]
    if since_date:
        event_tuples = [since_date <= event_tuple[0] for event_tuple in event_tuples]
    if until_date:
        event_tuples = [event_tuple[0] <= until_date for event_tuple in event_tuples]
    return [et[1] for et in event_tuples]


def getipaddress():
    return requests.get("http://ipecho.net/plain?").text


def parse_date_from_string(datetime_object):
    """Return datetime object as string."""
    return datetime.datetime.strptime(datetime_object, "%m-%d-%Y")


def get_dates_from_arguments(arguments):
    """Return triplet of dates from given arguments."""
    since_date, until_date, text_date = None, None, ""
    if arguments["since"]:
        since_date = parse_date_from_string(arguments["since"])
        text_date = "since {}".format(since_date)
    if arguments["until"]:
        until_date = parse_date_from_string(arguments["until"])
        if text_date == "":
            text_date = "until {}".format(until_date)
        else:
            text_date = "from {} to {}".format(since_date, until_date)
    return since_date, until_date, text_date


def show_contri(args=None):
    """Sends a get request to GitHub REST api and display data using the
    utility functions"""

    user = args["name"]
    today = str(datetime.datetime.now().strftime("%Y-%m-%d"))
    link = "{}{}/events".format(github_uri, str(user))
    response = requests.get(link)
    events = response.json()
    latest = []
    stars = []
    other = []

    text_date = ""
    # NOTE: This needs more work. Possibly creating its own class of some sorts.
    if response.status_code == 200:
        since_date, until_date, text_date = get_dates_from_arguments(args)
        events = filter_since_until_dates(events, since_date=since_date, until_date=until_date)

        if 'since_date' in vars() or 'until_date' in vars():
            latest, stars, other = fill_dated_data(
                user, events, latest, stars, other)
        else:
            latest, stars, other = fill_todays_data(
                user, today, events, latest, stars, other)

        if not args["np"]:
            get_basic_info(user)

        if args["org"]:
            get_contributions(user, latest, text_date, args["org"])
        else:
            get_contributions(user, latest, text_date)

        get_other_activity(user, other, text_date)
        display_stars(user, stars, text_date)
    else:
        error_messages = {
            404: "User with username {0} does not exists, please check and try again".format(user),
            403: ("API rate limit exceeded for IP address"
                  " {} Try again later or change IP adress.").format(getipaddress()),
        }
        fallback_error_message = ("Something went wrong, please check your internet connection \n"
                                  "Use stalk --help for Help")
        err_msg = error_messages.get(response.status_code, fallback_error_message)
        print(err_msg)


def run():
    """Parsing the command line arguments using argparse and calls the update
    or show_contri function as required"""

    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs='?', help="name of the user")
    ap.add_argument("--org", help="Organization Name")
    ap.add_argument(
        "-U", "--update",
        action='store_true',
        help="Update this program to latest version. "
             "Make sure that you have sufficient permissions \
             (run with sudo if needed)"
    )
    ap.add_argument(
        "-np", action='store_true',
        help="Stalks a user without showing their profile")
    ap.add_argument(
        "--since",
        help=(
            "Take into account only events since date. Date format MM-DD-YYYY")
    )
    ap.add_argument(
        "--until",
        help=(
            "Take into account only events until date. Date format MM-DD-YYYY")
    )
    args = vars(ap.parse_args(args=None if sys.argv[1:] else ['--help']))

    if len(args) > 1:
        if args["update"]:
            update()
        else:
            show_contri(args)
    else:
        print(
            "Enter a valid username to stalk. \n"
            "For eg: stalk aashutoshrathi \n"
            "Or you can type stalk --help for help")


if __name__ == '__main__':
    run()
