from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime
import re

def scrape_google_scholar_profile(profile_url):
    papers = []
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        driver.get(profile_url)
        
        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gsc_a_tr"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            for entry in soup.find_all('tr', class_='gsc_a_tr'):
                title_elem = entry.find('a', class_='gsc_a_at')
                authors_elem = entry.find('div', class_='gs_gray')
                venue_elem = entry.find_all('div', class_='gs_gray')
                year_elem = entry.find('td', class_='gsc_a_y')
                citation_elem = entry.find('td', class_='gsc_a_c')
                
                title = title_elem.text.strip() if title_elem else "N/A"
                authors = authors_elem.text.strip() if authors_elem else "N/A"
                year = year_elem.text.strip() if year_elem else "N/A"
                
                citation_count = "N/A"
                if citation_elem:
                    citation_match = re.search(r'\d+', citation_elem.text)
                    if citation_match:
                        citation_count = citation_match.group()
                
                venue = "N/A"
                if len(venue_elem) > 1:
                    venue = venue_elem[1].text.strip()
                
                papers.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': venue,
                    'citations': citation_count
                })
            
            try:
                show_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "gsc_bpf_more"))
                )
                if "disabled" in show_more.get_attribute("class"):
                    break
                show_more.click()
                time.sleep(2)
            except TimeoutException:
                break
    
    except Exception as e:
        print(f"An error occurred while scraping: {str(e)}")
    
    finally:
        if 'driver' in locals():
            driver.quit()
    
    return papers

def save_to_csv(papers, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'authors', 'year', 'venue', 'citations']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)



