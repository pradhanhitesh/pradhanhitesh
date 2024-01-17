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

def get_timestamp():
    t = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', t)

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

def arrange_metadata(search_terms):

    data = []
    for k in search_terms:
        search_terms,extracted_number =  get_metadata(k)
        data.append([search_terms,extracted_number])
    
    data_df = pd.DataFrame(data,columns=['Keywords','Count'])

    return data_df

def generate_plot(data_df,time):
    # Set defaults for plot
    plt.figure(figsize=(12,5))
    plt.xticks(range(len(data_df)), list(data_df['Keywords']), rotation=45)

    # Create barplots
    sns.barplot(data=data_df,x='Keywords',y='Count')
    ax = sns.barplot(data=data_df,x='Keywords',y='Count')
    ax.bar_label(ax.containers[0])
    txt = "Last updated on: " + str(time)
    plt.text(3.1, 269000, txt, fontsize = 16)

    # Save the figure
    plt.savefig('figure.png',bbox_inches='tight')
    plt.close()

    return

def generate_html_for_plot():
    all_files = os.listdir("./")
    png_files = [file for file in all_files if file.endswith('.png')]

    template_vars = {
        'plot' : f'<img src="{png_files[0]}" width="650" height="400">'
        }
    
    return template_vars