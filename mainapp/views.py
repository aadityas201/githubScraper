from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.base import View
from bs4 import BeautifulSoup
import requests
from requests import session
# Create your views here.
import csv
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()

BASE = "https://github.com"
profileUrls = []
Fieldname = ["Name", "githubHandle", "Blurb","Location" , "Email", "LinkToPRofile"]

def mysession():
    session = requests.session()
    session.headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'token ' + os.getenv('TOKEN'),
        'User-Agent': 'GithubEmailHarvest',
    }
    return session



class Home(View):
    def get(self,request):
        return render(request, 'index.html')
    def post(self,request):
        print(os.getenv('TOKEN'))
        out_file = open("putput.csv","w", encoding="utf-8")

        csv_write = csv.DictWriter(out_file, fieldnames=Fieldname, lineterminator="\n")
        csv_write.writeheader()
        data = request.POST

        search_field = data['search_term']
        location = data['location']
        language = data['language']

        if(search_field==""): 
            return render(request, 'index.html', context={'msg' : 'Search field is required'})
        if(location == ""):
            location = 'india'
        if(language==""):
            language = 'python'    
        q = f"{search_field} location:{location} language:{language}"
        # q = '{} language:{}'.format(search_field, language)
        params = {
            'q' : q,
        }
        session = mysession()
        res = session.get('https://api.github.com/search/users', params=params)
        print(res.url)
        # print(res.json())
        formatted_data = res.json()
        items = formatted_data.get('items')
        for item in items:
            profileUrls.append(item.get("login"))
        # print(profileUrls)
        for profile in profileUrls:
            url = f"https://api.github.com/users/{profile}"
            res2 = session.get(url)
            json_res = res2.json()
            row = {
                'Name' : json_res.get('name'),
                'githubHandle' : json_res.get('login'),
                'Blurb' : json_res.get('bio').strip(),
                'Location' : json_res.get('location'),
                'Email' : json_res.get('email'),
                'LinkToPRofile' : json_res.get('html_url')

            }
            pprint(row)
            csv_write.writerow(row)
            

        
        


        # q = f"{search_field} language:{language} location:{location}"
        # print(data)
        # if(len(search_field) and len(language) and len(language)):
        #     url = f"{BASE}/search?q={search_field}+location%3A{location}+language%3A{language}&type=users"
        #     r = requests.get(url)
        #     soup = BeautifulSoup(r.content, 'html.parser')
        #     bigboxes = soup.find_all("div", class_ = "hx_hit-user")

        #     for boxes in bigboxes:
        #         a = boxes.find("a", class_ = "mr-1")
        #         name = a.text
        #         link = a['href']
        #         blurb = boxes.find("p",class_ = "mb-1").text.strip()
        #         d = boxes.find("div", class_ = "mr-3").text.strip()

                
                # print(newUrl)
            #     # print(name)
            #     # print(link)
                
            # print(bigboxes)
        return render(request, 'index.html')
