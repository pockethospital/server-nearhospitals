from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import os

def rchop(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring

def downloadImage(url, file_name):
    file_path = 'telanaga-cities'

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    fullPath = file_path +'/'+ file_name+'_icon.jpg'
    urlretrieve(url,fullPath)
    return fullPath

def jsonFileCreate(title='', index=0, icon='', lastIndex=0, startFile=False, endFile=False):

    fileName= 'telanga-cities.json'
    file_path = 'telanaga-cities'
    fullpath = file_path+"/"+fileName

    if not os.path.exists(file_path):
        os.makedirs(file_path)

    saveFile = open(fullpath, 'a+', encoding='utf-8')


    if startFile:
        data = '{"cities": ['
        saveFile.write(data)
    elif endFile:
        data = ']}'
        saveFile.write(data)
    else:
        data = {
            "id": "telanagna-cities-"+str(index),
            "name": title,
            "icon": icon,
            "quick": False
        }
        data = str(data)
        maketrans = data.maketrans
        data = data.translate(maketrans('\'False', '"false'))

        if lastIndex == index:
            saveFile.write(str(data))
        else:
            saveFile.write(str(data)+",")

    saveFile.close()

def openFile(fileName):
    saveFile = open(fileName,'r', encoding='utf-8')

    html = saveFile.read()
    soup = BeautifulSoup( html, 'html.parser')

    # Logic
    cards = soup.find_all('a', class_="klitem")
    
    lastIndex = len(cards)
    jsonFileCreate(startFile=True)
    
    for index, card in enumerate(cards):
        title = card.find('div', class_="kltat").contents
        text = ""
        for data in title:
            if data.string:
                data = data.string
                data = data.replace(', ', ' ')        
                data = data.replace('district', '')        
                data = data.replace('India', '')        
                text += data
        text = text.strip()
        
        img = card.find('img').attrs.get('data-src')

        if not img:
            img = card.find('img').attrs.get('data-key')

        maketrans = text.maketrans
        icon = downloadImage(img, text.translate(maketrans(' ', '_')).lower())
        jsonFileCreate(title=text, index=index+1, icon=icon, lastIndex=lastIndex)
        print(title)
        print(text)
        print(img)

    jsonFileCreate(endFile=True)


    saveFile.close()


openFile('web.txt')

