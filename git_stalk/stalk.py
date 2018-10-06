import requests
import datetime
import re
import os
import argparse
from dateutil import tz
from prettytable import PrettyTable

github_uri = "https://api.github.com/users/"


def validate_datetime(date_text):
    """Validates date entered by user"""
    try:
        return datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def jft(user):
    user_link = github_uri + str(user)
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
    user_link = github_uri + str(user)
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


def get_contributions(user, latest, org=None, date_text="today"):
    """
        Traverses the latest array,
        creates a table
        if org argument is present only the repos which belong to the org is added to the table
        and prints the table.
    """
    print("Contributions " + date_text + ": ")
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
    print(user + " have made " + str(len(latest)) +
          " public contribution(s) " + date_text + ".\n")


def get_other_activity(user, other, date_text="today"):
    """
        Traverses the other array,   
        creates a table
        and prints the table.
    """
    print("Other Activity " + date_text + ": ")
    if other:
        other_table = PrettyTable(["Type", "Repository", "Time", "Details"])
        for event in other:
            other_table.add_row([
                get_event(event["type"]), event["repo"]["name"],
                get_local_time(event["created_at"]),
                get_details(event),
            ])
        print(other_table)
    print(user + " have done " + str(len(other)) +
          " other public activit(y/ies) " + date_text + ".\n")


def get_stars(user, stars, date_text):
    """
        Traverses the stars array,
        creates a table
        and prints the table.
    """
    print("Starred " + date_text + ": ")
    if stars:
        star_table = PrettyTable(["Repository", "Language", "Time"])
        for event in stars:
            star_table.add_row([event["repo"]["name"], get_details(
                event), get_local_time(event["created_at"])])
        print(star_table)
    print(user + " have starred " + str(len(stars)) + " repo(s) " +
          date_text + ".")


def fill_data(user, day, events, latest, stars, other):
    """Traverses the events array and seperates individual data to latest, stars and other arrays"""
    for event in events:
        starts_at_date = convert_to_local(event["created_at"]).startswith(day)
        event_type_issue_comment_event = event["type"] != "IssueCommentEvent"

        if starts_at_date and event_type_issue_comment_event:
            if event["type"] == "WatchEvent":
                stars.append(event)
            elif event["type"] in ("ForkEvent", "MemberEvent"):
                other.append(event)
            elif check_for_fork(event["repo"]["url"], user):
                latest.append(event)
    return latest, stars, other


def update():
    """Runs the upgrade command and upgrades git-stalk"""
    os.system("pip install --upgrade git-stalk")


def fetch_events(link):
    """Fetch data including pagination. Github API paginates until 300 results,
    that means we can have until 10 pages per request."""
    events = []
    for i in range(1, 10):
        current_page = requests.get(link + "?page=" + str(i))
        if current_page.status_code != 200 or current_page.text == '[]':
            break
        events += current_page.json()
    return events


def show_contri(args=None):
    """Sends a get request to github rest api and display data using the utility functions"""
    user = args["name"]
    if args["date"]:
        day = validate_datetime(args["date"])
        date_text = "at " + args["date"]
    else:
        day = datetime.datetime.now()
        date_text = "today"
    day_str = str(day.strftime("%Y-%m-%d"))
    link = github_uri + str(user) + "/events"
    events = fetch_events(link)
    latest = []
    stars = []
    other = []
    if events:
        latest, stars, other = fill_data(
            user, day_str, events, latest, stars, other)
    else:
        print(
            "Something went wrong, check your internet or username. \n"
            "Use stalk --help for Help"
        )
        return

    if args["np"] is False:
        get_basic_info(user)

    if args["org"]:
        get_contributions(user, latest, args["org"], date_text)
    else:
        get_contributions(user, latest, date_text=date_text)

    get_other_activity(user, other, date_text)
    get_stars(user, stars, date_text)


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
    ap.add_argument("--date",
                    help="Filter events in the select date (format YYYY-MM-DD)"
                    " whithin the past 90 days."
                    )
    ap.add_argument("-np", action='store_true',
                    help="Stalks a user without showing their profile")
    args = vars(ap.parse_args())

    if len(args) > 1:
        if args["update"]:
            update()
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
