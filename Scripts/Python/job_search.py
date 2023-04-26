import csv
import requests
import pandas as pd

from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = "http://www.indeed.com"

def get_url(position, location):
    """Generate url from position and location"""
    template = 'https://www.indeed.com/jobs?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url

def get_data(base_url):
    """Request data from base_url"""
    response = requests.get(base_url)
    return response.text

def source_data(complete_url):
    """Create beautifulsoup object"""
    sourceCode = get_data(complete_url)
    sourceSoup = BeautifulSoup(sourceCode, 'html.parser')
    return sourceSoup

def filter_data_list(sourceSoup):
    """Compiling list by finding all tables with the class resultContent"""
    # sourceList = sourceSoup.find_all("resultContent")
    # return sourceList

    #rel_soup = sourceSoup.td['class']
    #return rel_soup

def filter_data_links(sourceList):
    """Iterate through the list to locate the links"""
    source_links = []
    for list in sourceList:
        source_list = list.find_all('a')
        for a in source_list:
            if a.text != '':
                source_links.append(BASE_URL + a['href'])
    return source_links

if __name__ == '__main__':
    myUrl = get_url("System Engineer", "New York")
    myData = get_data(myUrl)
    myCompiled = source_data(myUrl)
    myList = filter_data_list(myCompiled)
    data = filter_data_links(myList)
    print(data)