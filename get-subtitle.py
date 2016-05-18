from requests import get
from bs4 import BeautifulSoup
import re
import zipfile
import os

def get_movie_info(release_name):

	#movie name format
	#Title.Of.The.Movie.YEAR.Source.Codec-GROUP 
	#https://en.wikipedia.org/wiki/Standard_%28warez%29#Naming

	#use regex to extract movie info

	info={'name':release_name,'year':"",'season':"",'quality':""}
	k=len(release_name)
	year=re.search(r'([ \(\.])([0-9]{4})([ \)\.])',release_name,re.I)
	if(year):
		k=release_name.find(year.group())
		year=re.search(r'[0-9]+',year.group(),re.I)
		info['year']=year.group()
		release_name=release_name.replace(year.group(),"")
	season=re.search(r'(s?)[0-9]+(\.?)(x|e|)[0-9]+',release_name,re.I)
	if(season):
		tvflag=1
		info['season']=season.group()
		k=release_name.find(season.group())
		release_name=release_name.replace(season.group(),"")
	quality=re.search(r'([0-9]+)(p)',release_name,re.I)
	if(quality):
		info['quality']=quality.group()
		release_name=release_name.replace(quality.group(),"")
		

	#clean the movie name

	info['name']=release_name[:k].strip()

	return info


filepath=raw_input("Enter your filepath: ")

dirpath=""
filename=""
j=0
l=len(filepath)
tvflag=0


for i in range(0,l):
	filename+=filepath[i]
	if(filepath[i]=='\\'):
		dirpath+=filename
		filename=""
	if(filepath[i]=='.'):
		j=l-i
#removing format name
filename=filename[:len(filename)-j] 

file_info=get_movie_info(filename)

url="https://subscene.com/subtitles/release?q="+filename
response=get(url)
soup=BeautifulSoup(response.text,"html.parser")
tr=soup.find_all('td',class_='a1')
max_score=-1
href=""

for td in tr:
	info=td.find_all('span')
	language=info[0].find(text=True).strip()
	release_name=info[1].find(text=True).strip()
	score=0
	if(language=="English"):
		
		movie_info=get_movie_info(release_name)
		#match movie metadata with our file's metadata

		if(file_info['name']==movie_info['name']):
			score+=1
		else:
			score=-3
		if(file_info['season']==movie_info['season']):
			#need to handle season number and episode number...too lazy
			score+=1
		if(file_info['year']==movie_info['year']):
			score+=1
		if(file_info['quality']==movie_info['quality']):
			score+=1

		if(score>max_score):
			max_score=score
			href=td.find('a').get("href").strip()

if(max_score==0):
	print("NOT FOUND")
	exit()

print ("SUBTITLES FOUND")

subtitle_url="http://subscene.com"+href
response=get(subtitle_url)
soup=BeautifulSoup(response.text,"html.parser")
download_href=soup.find('a', {"id": "downloadButton"}).get("href").strip()

download_url="http://subscene.com"+download_href
response=get(download_url)

with open(dirpath+filename+".zip","wb") as file:	
	file.write(response.content)
file.close()

print ("ZIP DOWNLOADED")
zfile = zipfile.ZipFile(dirpath+filename+".zip","r")
subtitle_file_name=zfile.namelist()[0]
zfile.extractall(dirpath)
os.rename(dirpath+subtitle_file_name,dirpath+filename+".srt")
zfile.close()
os.remove(dirpath+filename+".zip")

print("DONE")





