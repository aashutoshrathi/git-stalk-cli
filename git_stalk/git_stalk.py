try:
   from urllib.request import urlopen
except ImportError:
   from urllib2 import urlopen
from bs4 import BeautifulSoup
import datetime
import sys

def show_contri(user):
    contri = 0
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    link = "https://github.com/" + str(user)
    page = urlopen(link)
    soup = BeautifulSoup(page, 'html.parser')
    try:
        boxes = soup.find_all('rect', attrs={"data-date" : today})
        contri = boxes[0]["data-count"]
    except:
        raise Exception("Either user doesn't exist or you no contributions are made today.")
    return (user + " have made " + str(contri) + " contributions today.")

def run():
	if len(sys.argv) > 1:
		print(show_contri(sys.argv[1]))
	else:
		print("Enter a valid username")

if __name__ == '__main__':
	run()