import time, openpyxl, xlsxwriter, urllib, logging, requests
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.WARNING)

JOB_BOARD_URL_PARAMS = {
    "indeed": {"url": "https://www.indeed.com", "query_param": "q", "location_param": "l", "location_type": "postal"},
    "linkedin": {"url": "https://www.linkedin.com/jobs", "query_param": "keywords", "location_param": "location", "location_type": "city"},
    "monster": {"url": "https://www.monster.com", "query_param": "q", "location_param": "where", "location_type": "city"}
}

def search_jobs_boards(job_board: str, position: str, salary: int, city_state: str,
                       radius: int, zipcode: str, fromage: int) -> List[Dict[str, str]]:
    # Retrieve job board query parameters from dict
    params = JOB_BOARD_URL_PARAMS.get(job_board)
    if not params:
        logging.warning(f"{job_board} is not a supported job board.")
        return []

    # Construct URL
    base_url = f"{params['url']}/jobs"
    query = urllib.parse.urlencode({params['query_param']: position + f" ${salary}"})
    location = urllib.parse.quote_plus(city_state)

    if params.get('location_type') == 'postal':
        location_params = f"&radius={radius}&postal={zipcode}"
    elif params.get('location_type') == 'city':
        location_params = f"&radius={radius}"
    else:
        location_params = ''

    url = f"{base_url}?{query}&{params['location_param']}={location}{location_params}&fromage={fromage}"
    logging.debug(f"{job_board}.....{url}")

    # Search for job listings
    with webdriver.Chrome() as driver:
        driver.get(url)
        WebDriverWait(driver, 5)

        try:
            # Extract job listings
            job_listings = driver.find_elements(By.CLASS_NAME, "resultContent")
            results = []
            for job_listing in job_listings:
                try:
                    job_title_element = job_listing.find_element(By.TAG_NAME, "span")
                    job_title = job_title_element.text
                except Exception as e:
                    logging.warning(f"Failed to find job title: {e}")
                    job_title = ""

                try:
                    job_url_element = job_listing.find_element(By.CLASS_NAME, "jcs-JobTitle")
                    job_id = job_url_element.get_attribute('id')
                    job_url = job_url_element.get_attribute('href')
                except Exception as e:
                    logging.warning(f"Failed to find job URL or ID: {e}")
                    job_id, job_url = "", ""

                try:
                    job_location = job_listing.find_element(By.CLASS_NAME, "companyLocation").text
                except Exception as e:
                    logging.warning(f"Failed to find job location: {e}")
                    job_location = ""

                try:
                    job_company = job_listing.find_element(By.CLASS_NAME, "companyName").text
                except Exception as e:
                    logging.warning(f"Failed to find job company: {e}")
                    job_company = ""

                try:
                    job_salary = job_listing.find_element(By.CLASS_NAME, "salaryOnly").text
                except Exception as e:
                    logging.warning(f"Failed to find job salary: {e}")
                    job_salary = ""

                # Store results
                results.append({
                    'job_id': job_id,
                    'job_title': job_title,
                    'job_salary': job_salary,
                    'job_url': job_url,
                    'job_location': job_location,
                    'job_company': job_company,
                    'job_board': job_board,
                })
        except Exception as e:
            logging.error(f"Error occurred while scraping job listings from {job_board}: {e}")
            results = []

    return results

def export_to_excel(results: List[Dict[str, str]], position: str) -> None:
    """
    Exports job listing information to an Excel file with the given position in the file name.
    """
    # Define the output filename
    output_filename = f"{position}_jobs.xlsx"
    
    # Create an Excel workbook and worksheet
    workbook = xlsxwriter.Workbook(output_filename)
    worksheet = workbook.add_worksheet()
    
    # Write the header row
    header_format = workbook.add_format({'bold': True})
    header_row = ['Job Title', 'Company', 'Location', 'Salary', 'URL']
    for i, header in enumerate(header_row):
        worksheet.write(0, i, header, header_format)
    
    # Write the data rows
    for row, result in enumerate(results, start=1):
        worksheet.write(row, 0, result['job_title'])
        worksheet.write(row, 1, result['job_company'])
        worksheet.write(row, 2, result['job_location'])
        worksheet.write(row, 3, result['job_salary'])
        worksheet.write(row, 4, result['job_url'])
    
    # Close the workbook
    workbook.close()
    
    print(f"Exported {len(results)} job listings to {output_filename}")

def import_from_excel(position):
    """
    Import data from an Excel spreadsheet for a specific sheet name
    and return it as a list of dictionaries, where each dictionary
    represents a row of data.
    """
    input_filename = f"{position}_jobs.xlsx"
    try:
        workbook = openpyxl.load_workbook(filename=input_filename)
        sheet = workbook['Sheet1']
    except FileNotFoundError:
        print(f"Error: file {input_filename} not found. Please rerun the script to generate the xlsx file")
        return None
    except KeyError:
        print(f"Error: sheet1 not found in {input_filename}. You may have altered the xlsx file. Please rerun the script to generate the xlsx file")
        return None

    headers = [cell.value for cell in next(sheet.iter_rows())]
    data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        data.append(dict(zip(headers, row)))

    return data

def get_job_urls(datafile):
    job_urls = []
    for data in datafile:
        for key, value in data.items():
            if key == 'URL':
                job_urls.append(value)

    return job_urls

def apply_to_job(job_urls):
    pass

if __name__ == '__main__':
    # Enter the position, city/state, and radius (in miles) around a zip code to search
    job_board = "indeed"
    position = "System Administrator"
    salary = 90000
    city_state = "New York, NY"
    radius = 35
    zipcode = "07109"
    fromage = 14
    results = search_jobs_boards(job_board, position, salary, city_state, radius, zipcode, fromage)
    export_to_excel(results, position)
    job_search_doc = import_from_excel(position)
    get_job_urls(job_search_doc)