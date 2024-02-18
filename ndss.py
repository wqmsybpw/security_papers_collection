from io import TextIOWrapper
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import codecs
import json

base_url = "https://www.ndss-symposium.org/"

def get_hrefs(year):
    index = "ndss" + str(year) + "/accepted-papers/"
    url = base_url + index
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    hrefs = soup.find_all(attrs={"class" :"paper-link-abs"})
    return hrefs

def get_papers(year, output: TextIOWrapper):
    hrefs = get_hrefs(year)
    results = []
    for href in tqdm(hrefs):
        url = href['href']
        while True:
            try:
                response = requests.get(url, timeout=10)
                break
            except Exception:
                print("Retry...")
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find_all(attrs={"class" :"entry-title"})[0].text
        abstract = soup.find_all(attrs={"class" :"paper-data"})[0].contents[3].text
        pdf = soup.find_all(attrs={"class" :"btn btn-light btn-sm pdf-button"})[0]['href']
        print(title)
        results.append({"title": title, "pdf": pdf, "abstract": abstract})
    output.write(json.dumps(results, ensure_ascii=False, indent=4))

#get_papers(2024, codecs.open("ndss2024.txt", "w", encoding="utf-8"))
#get_papers(2023, codecs.open("ndss2023.txt", "w", encoding="utf-8"))
get_papers(2022, codecs.open("ndss2022.txt", "w", encoding="utf-8"))
