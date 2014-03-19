#!/usr/bin/env python
from PIL import Image
import sys
import commands
import hashlib
import time
import math
import os
import requests
import BeautifulSoup


class VectorCompare:
  def magnitude(self,concordance):
    total = 0
    for word,count in concordance.iteritems():
      total += count ** 2
    return math.sqrt(total)

  def relation(self,concordance1, concordance2):
    relevance = 0
    topvalue = 0
    for word, count in concordance1.iteritems():
      if concordance2.has_key(word):
        topvalue += count * concordance2[word]
    return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))

def buildvector(im):
  d1 = {}
  count = 0
  for i in im.getdata():
    d1[count] = i
    count += 1
  return d1

img_name = 'rand.jpeg'
# fetch the captcha image and set the cookie
req = requests.request('GET', 'http://www.ems.com.cn/ems/rand')
cookies = req.cookies
print cookies
handle = open(img_name, 'w')
handle.write(req.content)
handle.close()

# open captcha image from requests
col = Image.open(img_name)
gray = col.convert('L')
bw = gray.point(lambda x: 0 if x<128 else 255, '1')

inletter = False
foundletter=False
start = 0
end = 0

letters = []

for y in range(bw.size[0]): # slice across
  for x in range(bw.size[1]): # slice down
    pix = bw.getpixel((y,x))
    if pix != 255:
      inletter = True
  if foundletter == False and inletter == True:
    foundletter = True
    start = y

  if foundletter == True and inletter == False:
    foundletter = False
    end = y
    letters.append((start,end))

  inletter=False
print letters


count = 0
for letter in letters:
  m = hashlib.md5()
  im3 = bw.crop(( letter[0] , 0, letter[1],bw.size[1] ))
  m.update("%s%s"%(time.time(),count))
  #im3.save("./%s.png"%(m.hexdigest()))
  count += 1

v = VectorCompare()

iconset =  ['0','1','2','3','4','5','6','7','8','9','0']
imageset = []

for letter in iconset:
  for img in os.listdir('./iconset/%s/'%(letter)):
    temp = []
    if img != "Thumbs.db":
      temp.append(buildvector(Image.open("./iconset/%s/%s"%(letter,img))))
    imageset.append({letter:temp})


count = 0
captcha = ""
for letter in letters:
  m = hashlib.md5()
  im3 = bw.crop(( letter[0] , 0, letter[1],bw.size[1] ))

  guess = []

  for image in imageset:
    for x,y in image.iteritems():
      if len(y) != 0:
        guess.append( ( v.relation(y[0],buildvector(im3)),x) )
  guess.sort(reverse=True)
  print "",guess[0]
  captcha += str(guess[0][1])
  count += 1
print captcha

payload = {'muMailNum':'1128081891901','checkCode':captcha}
headers = {'Referer' : 'http://www.ems.com.cn/mailtracking/you_jian_cha_xun.html', 'Cookie' : cookies, }
req = requests.post('http://www.ems.com.cn/ems/order/singleQuery_t', headers = headers, data=payload)
print req.headers
html = open('index.html', 'w')
html.write(req.content)
html.close()
