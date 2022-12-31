import requests
from bs4 import BeautifulSoup
import csv
import json
import sys
import uuid
import base64
from itertools import zip_longest

article_ID = []
article_title = []
article_description = []
article_dom = []
published_date = []
article_link = []
website_name = []

result = requests.get("https://www.arabmediasociety.com/category/features/")
# save page content/markup
src = result.content
soup = BeautifulSoup(src, "lxml")

article_titles = soup.find_all("h2", {"class": "post-box-title"})
article_descriptions = soup.find_all("div", {"class": "entry"})

# looping to make info lists
for i in range(len(article_titles)):
    article_title.append(article_titles[i].find("a").text)
    article_link.append(article_titles[i].find("a").attrs['href'])
    article_description.append(article_descriptions[i].find("p").text)
    article_ID.append(base64.urlsafe_b64encode(
        uuid.uuid1().bytes).rstrip(b'=').decode('ascii'))


# get needed info from every article
for link in article_link:
    result = requests.get(link)
    src = result.content
    soup = BeautifulSoup(src, "lxml")
    article_dom.append(soup.find("body"))
    published_date.append(soup.find_all("span", {"class": "tie-date"})[0].text)

file_list = [article_ID, article_title, article_description,
             article_dom, published_date, article_link]
exported = zip_longest(*file_list)
with open("./data.csv", "w", newline='', encoding="utf-8") as myData:
    wr = csv.writer(myData)
    wr.writerow(["article_ID", "article_title", "article_description",
                "article_dom", "published_date", "article_link"])
    wr.writerows(exported)

# make json from the CSV file
def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []

    with open(csvFilePath, encoding='utf-8') as csvf:
        maxInt = sys.maxsize

        while True:
            # decrease the maxInt value by factor 10
            # as long as the OverflowError occurs.
            try:
                csv.field_size_limit(maxInt)
                break
            except OverflowError:
                maxInt = int(maxInt/10)
                # load csv file data using csv library's dictionary reader
                csvReader = csv.DictReader(csvf)
        # convert each csv row into python dict
        for row in csvReader:
            # add this python dict to json array
            jsonArray.append(row)
    # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


csvFilePath = r'./data.csv'
jsonFilePath = r'./data.json'
csv_to_json(csvFilePath, jsonFilePath)
