from bs4 import BeautifulSoup
from urllib.request import urlretrieve

def downloadImage(url, file_path, file_name):
    fullPath = file_path +'/'+ file_name+'_icon.jpg'
    urlretrieve(url,fullPath)
    return
saveFile = open('noheaders.txt','r', encoding='utf-8')

html = saveFile.read()
soup = BeautifulSoup( html, 'html.parser')
imgs = soup.find_all('g-img', class_="BA0A6c")
titles = soup.find_all('div', class_="kltat")
print(len(imgs))
print(len(titles))

mainCities = []
for item in range(51):
    imageKeyURL = imgs[item].find('img').attrs.get('data-key')
    imageSrcURL = imgs[item].find('img').attrs.get('data-src', imageKeyURL)
    title = titles[item].find('span').string
    print(imageSrcURL)
    print(title)
    title = title.strip(" ,")
    maketrans = title.maketrans 

    downloadImage(imageSrcURL, 'topcities', title.translate(maketrans(' ', '_')).lower())

saveFile.close()



#pip install textblob bs4 requests
