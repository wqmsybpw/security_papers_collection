import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import codecs

base_url = "https://www.usenix.org/conference/usenixsecurity"
summer = "/summer-accepted-papers"
fall = "/fall-accepted-papers"
winter = "/winter-accepted-papers"

def get_pdf(url):
    while True:
        try:
            response = requests.get(url, timeout=10)
            break
        except Exception:
            print("Retry...")
    soup = BeautifulSoup(response.text, "html.parser")
    files = soup.find_all(attrs={"class": "file"})
    # 如果files为空，直接返回"not yet available"
    if not files:
        return "not yet available"
    official_link = ""
    prepublication_link = ""
    for file in files:
        # 检查每个file下是否有<a>标签，如果没有，继续下一个循环
        a_tag = file.find('a')
        if not a_tag:
            continue
        if 'Prepublication' in file.text:
            prepublication_link = a_tag['href']
    
    # 至少第一个肯定是论文
    t = files[0].find('a')
    if t:
        if 'Prepublication' not in t.text:
            official_link = t['href']

    if official_link:
        return official_link
    elif prepublication_link:
        return prepublication_link
    else:
        return "not yet available"

def get_papers_by_url(url):
    titles = []
    paper_urls = []
    abstracts = []
    pdfs = []
    results = []

    while True:
        try:
            response = requests.get(url, timeout=10)
            break
        except Exception:
            print("Retry...")
    if response.status_code == 404:
        print(f'{url} not exist.')
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all('article', class_='node node-paper view-mode-schedule')

    for article in articles:
        # 提取标题和链接
        title_tag = article.find('h2', class_='node-title').find('a')
        titles.append(title_tag.text.strip())
        paper_urls.append('https://www.usenix.org' + title_tag['href'])

        # 提取摘要
        abstract_tag = article.find('div', class_='field field-name-field-paper-description-long field-type-text-long field-label-hidden')
        abstract_text = ' '.join(p.text for p in abstract_tag.find_all('p')) if abstract_tag else ''
        abstracts.append(abstract_text.strip())
    
    for url in tqdm(paper_urls):
        pdfs.append(get_pdf(url))

    for i in range(len(titles)):
        results.append({"title": titles[i], "pdf": pdfs[i], "abstract": abstracts[i]})

    return results

def get_papers(year, output):
    index = int(year) - 2000
    conference_url = base_url + str(index)
    
    summer_papers = get_papers_by_url(conference_url + summer)
    fall_papers = get_papers_by_url(conference_url + fall)
    winter_papers = get_papers_by_url(conference_url + winter)
    
    papers = summer_papers + fall_papers + winter_papers

    output.write(json.dumps(papers, ensure_ascii=False, indent=4))

#get_papers(2024, codecs.open("usenix2024.txt", "w", encoding="utf-8"))
#get_papers(2023, codecs.open("usenix2023.txt", "w", encoding="utf-8"))
get_papers(2022, codecs.open("usenix2022.txt", "w", encoding="utf-8"))
