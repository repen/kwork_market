import requests, re
# import requests_cache
from bs4 import BeautifulSoup
from tools import log, hash_

log = log("model", "model.log")
# requests_cache.install_cache("demo_cache")

class Project:
    def __init__(self, *args):
        self.title = args[0]
        self.description = args[1]
        self.author = args[2]
        self.proposal_count = args[3]
        self.price = args[4]
        self.timer = args[5]
        self.link  = args[6]

    def __str__(self):
        string = "{}\n\n{}\n\nPrice: {}\nLink: [on project]({})".format(
            self.title, self.description[:3000], self.price, self.link
        )
        end =  "\n" + ("=" * 20)
        string += end
        return string

    def hash(self):
        return hash_(self.link)



url = "https://kwork.ru/projects"
headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) \
                                            Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)'}

def get_projects():
    projects = []
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup( html, "html.parser" )
    items = soup.select("div[class*=js-card]")
    for item in items[:]:
        title = item.select_one("div[class*=header-title]")
        title = title.text if title else "Error title"
        price = item.select_one("div.wants-card__right")
        price = re.findall( r"\d{3}|\d{1,2}\s\d{3}", str(price) )
        price = " - ".join(price)
        description = item.select_one("div.breakwords.hidden")
        description = description.text.replace("Скрыть","").strip() if description else "Description error"
        if description == "Description error":
            description = item.select_one("div.breakwords.first-letter").text if description else "Description error2"
        proposal_count = item.find(lambda tag:tag.name == "span" and "Предложений:" in tag.text)
        proposal_count = re.findall(r"\d+", proposal_count.text)[0] if proposal_count else "Prop error"
        author = item.select_one("a.v-align-t")
        author = author.text if author else "Author error"
        link = item.select_one("div.wants-card__header-title a")
        link = link['href'] if link else "Link error"
        timer = item.find( lambda tag:tag.name == "span" and "Осталось" in tag.text)
        timer = timer.text if timer else "timer error"
        params = (title, description, author, proposal_count,
                  price, timer, link)
        project = Project( *params )
        projects.append( project )
    return projects

projects = get_projects
