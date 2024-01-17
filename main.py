import re
import requests
import smtplib
from email.message import EmailMessage
from bs4 import BeautifulSoup
import datetime
import os
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from jinja2 import Template
import plotly.express as px

# Define time function
def get_timestamp():
    t = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', t)

# Send a request to the URL
def get_articles(search_terms):
    #print("Last updated:",get_timestamp())
    
    url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + search_terms +'&sort=date'
    response = requests.get(url)
    response.raise_for_status()

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    href_tags = soup.find_all(href=True)

    # mydivs = soup.find_all("div", {"class": "stylelistrow"})
    mydivs = soup.find_all("span", {"class": "value"})

    import re

    text = str(mydivs[0])
    pattern = r'<span class="value">([\d,]+)</span>'

    match = re.search(pattern, text)

    if match:
        extracted_number = match.group(1)
        # Remove commas from the extracted number
        extracted_number = extracted_number.replace(',', '')
        extracted_number = int(extracted_number)
        #print("Search terms:",search_terms, "Articles found:",extracted_number)

    return search_terms,extracted_number

search_terms = ["dementia","dementia+alzheimers","alzheimers","alzheimers+disease","dementia+MRI","alzheimers+MRI",
                "dementia+alzheimers+MRI"]

data = []
for k in search_terms:
    search_terms,extracted_number =  get_articles(k)
    data.append([search_terms,extracted_number])
data_df = pd.DataFrame(data,columns=['Keywords','Count'])

plt.figure(figsize=(12,5))
plt.xticks(range(len(data_df)), list(data_df['Keywords']), rotation=45)
sns.barplot(data=data_df,x='Keywords',y='Count')
txt = "Last updated on: " + str(get_timestamp())
plt.text(3.1, 269000, txt, fontsize = 16)
plt.savefig('figure.png',bbox_inches='tight')
plt.close()

all_files = os.listdir("./")
png_files = [file for file in all_files if file.endswith('.png')]

# <img src="{png_file}" width="600" height="400">
template_vars = {
    'time' : get_timestamp(),
    'search_terms' : 'dementia+AD',
    'extracted_number' : 26700,
    'plot' : f'<img src="{png_files[0]}" width="600" height="300">'

}

env = Environment(loader=FileSystemLoader("template"))
template = env.get_template("template.html")
output_from_parsed_template = template.render(template_vars)

with open("README.md", "w+") as fh:
    fh.write(output_from_parsed_template)