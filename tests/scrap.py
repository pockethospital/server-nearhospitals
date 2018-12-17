import requests
from bs4 import BeautifulSoup


class Analysis:

    def __init__(self, term):
        self.term = term
        self.subjectivity = 0
        self.sentiment = 0

        # self.url = 'https://www.google.com/search?q={0}&source=lnms&tbm=nws'.format(self.term)
        self.url = 'https://www.google.com/search?q={0}'.format(self.term)
        # self.url = "https://www.google.co.in/search?q=top+cities+in+india&oq=top+cities+in+india"
    
    def run(self):
        response = requests.get(self.url)
        # print(response.text)
        saveFile = open('noheaders.txt','r', encoding='utf-8')
        saveFile.write(str(response.text))
        saveFile.close()
        soup = BeautifulSoup(response.text, 'html.parser')
        headline_results = soup.find_all('div', class_="MiPcId")

        for h in headline_results:
            print(h)
a = Analysis('top+cities+in+india')
a.run()
