from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve

def downloadImage(url, file_name):
  file_path='states'
  if not os.path.exists(file_path):
    os.makedirs(file_path)
  fullPath = file_path +'/'+ file_name+'_icon.jpg'
  urlretrieve(url,fullPath)
  return fullPath

def createJsonData(stateID='', name='', imgPath='', quick=False, index=0, startFile=False, endFile=False):
  file_path='states'

  if not os.path.exists(file_path):
    os.makedirs(file_path)

  jsonFile = open(file_path+'/jsonFile.json', 'a+', encoding='utf-8')
  
  if startFile:
    data = '{"cities": ['
  elif endFile:
    data =  ']}'
  else:
    index = index+1
    data = {
      "id": "telengana-city-"+str(index),
      "name": name.title(),
      "state_id": stateID,
      "icon": imgPath,
      "quick": quick
    }

  jsonFile.write(str(data)+",")  
  jsonFile.close()
  return


saveFile = open('noheaders.txt','r', encoding='utf-8')
html = saveFile.read()
soup = BeautifulSoup( html, 'html.parser')
imgs = soup.find_all('g-img', class_="BA0A6c")
titles = soup.find_all('div', class_="S20Xzc")

print(len(imgs))
print(len(titles))

createJsonData(startFile=True, endFile=False)

for item in range(34):
  imageKeyURL = imgs[item].find('img').attrs.get('src')
  # imageSrcURL = imgs[item].find('img').attrs.get('data-src', imageKeyURL)
  titleData = titles[item].contents
  title = ""
  print(imageKeyURL)
  for div in titleData:
    title += div.string
  print(title)
  # title = title.strip(" ,")
  maketrans = title.maketrans 


  filePath = downloadImage(imageKeyURL, title.translate(maketrans(' ', '_')).lower())
  createJsonData(stateID='36', name=title, imgPath=filePath, quick=False, index=item)

createJsonData(startFile=False, endFile=True)

saveFile.close()



#pip install textblob bs4 requests
