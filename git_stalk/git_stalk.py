try:
   from urllib.request import urlopen
except ImportError:
   from urllib2 import urlopen
from bs4 import BeautifulSoup
import datetime

def show_contri(user):
    contri = 0
    now = datetime.datetime.now()
    today = str(now.strftime("%Y-%m-%d"))
    link = "https://github.com/" + str(user)
    page = urlopen(link)
    soup = BeautifulSoup(page, "html5lib")
    try:
        boxes = soup.find_all('rect', attrs={"data-date" : today})
        contri = boxes[0]["data-count"]
    except:
        raise Exception("Either user doesn't exist or you no contributions are made today.")
    return (int(contri))