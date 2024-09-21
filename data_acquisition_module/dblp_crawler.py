# File: data_acquisition_module/dblp_crawler.py

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re

def scrape_dblp_profile(profile_url):
    publications = []
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(profile_url)
        
        while True:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "entry"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            for entry in soup.find_all('li', class_='entry'):
                year = entry.find_previous('h2').text.strip()
                pub_type = 'Conference' if entry.find('img', alt='Conference and Workshop Papers') else 'Journal'
                
                title_elem = entry.find('span', class_='title')
                title = title_elem.text.strip() if title_elem else "N/A"
                
                authors = [author.text.strip() for author in entry.find_all('span', itemprop='author')]
                
                venue_elem = entry.find('span', itemprop='isPartOf')
                venue = venue_elem.text.strip() if venue_elem else "N/A"
                
                link_elem = entry.find('a', class_='publ')
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else "N/A"
                
                citation_elem = entry.find('span', class_='citations')
                citation_count = 0
                if citation_elem:
                    citation_match = re.search(r'\d+', citation_elem.text)
                    if citation_match:
                        citation_count = int(citation_match.group())
                
                publications.append({
                    'title': title,
                    'authors': ', '.join(authors),
                    'year': year,
                    'venue': venue,
                    'type': pub_type,
                    'link': link,
                    'citations': citation_count
                })
            
            try:
                show_more = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "publ-list-menu-endbody"))
                )
                if "disabled" in show_more.get_attribute("class"):
                    break
                show_more.click()
                time.sleep(2)
            except TimeoutException:
                break
    
    except Exception as e:
        print(f"An error occurred while scraping the DBLP profile: {e}")
    
    finally:
        driver.quit()
    
    return publications