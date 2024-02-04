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
import json
import pytz

def get_timestamp():
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    format_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return format_time

def get_metadata(search_terms):

    # Set the PubMed URL    
    url = 'https://pubmed.ncbi.nlm.nih.gov/?term=' + search_terms +'&sort=date'
    response = requests.get(url)
    response.raise_for_status()

    # Parse the content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    href_tags = soup.find_all(href=True)
    mydivs = soup.find_all("span", {"class": "value"})

    # Extract the number of articles for the keyword_search
    text = str(mydivs[0])
    pattern = r'<span class="value">([\d,]+)</span>'
    match = re.search(pattern, text)

    if match:
        extracted_number = match.group(1)
        # Remove commas from the extracted number
        extracted_number = int(extracted_number.replace(',', ''))

    return search_terms,extracted_number

def add_element(dict, key, value):
    if key not in dict:
        dict[key] = []
    dict[key].append(value)

def arrange_metadata(search_terms):

    data = []
    data_dict = {}
    add_element(data_dict,'Timestamp',get_timestamp())
    for k in search_terms:
        search_terms,extracted_number =  get_metadata(k)
        add_element(data_dict,search_terms,extracted_number)
        data.append([search_terms,extracted_number])
    
    data_df = pd.DataFrame(data,columns=['Keywords','Count'])
    data_df = data_df.sort_values(by='Count',ascending=False)

    return data_df,data_dict

def update_pubmed_json(data_dict):
    with open("data/pubmed.json") as doc:
        docObj = json.load(doc)
        docObj.append(
            data_dict
        )
    with open("data/pubmed.json", 'w') as json_file:
        json.dump(docObj, json_file, 
                  indent=4,  
                  separators=(',',': '))
    return

def generate_plot(data_df,time):
    # Set defaults for plot
    plt.figure(figsize=(12,5))
    plt.xticks(range(len(data_df)), list(data_df['Keywords']), rotation=45)

    # Create barplots
    ax = sns.barplot(data=data_df,x='Keywords',y='Count')
    ax.bar_label(ax.containers[0])
    # txt = "Last updated on: " + str(time) + " UTC"
    # plt.text(2.6, 269000, txt, fontsize = 16)
 
    # Save the figure
    plt.savefig('figure.png',bbox_inches='tight')
    plt.close()

    return

def generate_html_for_plot():
    all_files = os.listdir("./")
    png_files = [file for file in all_files if file.endswith('.png')]

    template_vars = {
        'plot' : f'<img src="{png_files[0]}" width="700" height="400">',
        'timestamp' : get_timestamp()
        }
    
    return template_vars