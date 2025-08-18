import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from urllib.parse import urljoin, quote
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
from typing import Dict, List, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# FULL CROP CATEGORIES - All crops enabled
CROP_CATEGORIES = {
    'agriculture': {
        'cereals': [
            'barley-jow', 'maize-kharif', 'maize-rabi', 'oats', 
            'pearl-millet', 'rice', 'wheat-kanak-gehu'
        ],
        'fibre-crops': [
            'cotton'
        ],
        'fodder': [
            'bajra-napier-hybrid', 'berseem', 'finger-millet', 'guar',
            'guinea-grass', 'lucerne', 'senji-hybrid', 'shaftal',
            'sorghum', 'teosinte'
        ],
        'green-manure': [
            'cowpea', 'dhaincha', 'mesta', 'sunhemp'
        ],
        'oilseeds': [
            'groundnut', 'linseed-flax', 'mustard', 'safflower',
            'soybean', 'sunflower'
        ],
        'pulses': [
            'lentil-masur', 'bengal-gram-chickpea', 'green-gram-moong',
            'kidney-bean-rajma', 'mash-urd', 'pigeon-pea-tur', 'rice-bean'
        ],
        'sugar-and-starch-crops': [
            'sugarcane'
        ],
        'citrus': [
            'lemon', 'lime-nimboo'
        ]
    },
    'horticulture': {
        'flowers': [
            'carnation', 'chrysanthemum', 'gerbera', 'gladiolus',
            'jasmine', 'marigold', 'rose', 'tuberose-rajnigandha'
        ],
        'forestry': [
            'drek', 'eucalyptus', 'poplar', 'sagwan'
        ],
        'fruit': [
            'banana', 'ber', 'date-palm', 'grapes', 'guava', 'jamun',
            'kinnow', 'litchi', 'loquat', 'mango', 'mulberry', 'muskmelon',
            'orange-mandarins-santra', 'papaya', 'peach', 'pear-nashpati',
            'plum', 'pomegranate', 'sapota', 'sweet-oranges-malta', 'watermelon'
        ],
        'medicinal-plants': [
            'aloe-vera', 'amla', 'ashwagandha', 'bahera', 'bhumi-amalaki',
            'brahmi', 'dill-seeds', 'honey', 'indian-bael', 'kalihari',
            'lemon-grass', 'mulethi', 'neem', 'pudina', 'sadabahar',
            'safed-musli', 'sarpagandha', 'shankhpushpi', 'shatavari',
            'stevia', 'sweet-flag', 'tulsi'
        ],
        'plantation-crops': [
            'fig'
        ],
        'spice-and-condiments': [
            'coriander', 'fennel', 'fenugreek', 'ginger-adrakh', 'turmeric-haldi'
        ],
        'vegetable-crops': [
            'arum-arvi', 'ash-gourd', 'beetroot', 'bitter-gourd',
            'bottle-gourd', 'brinjal', 'broccoli', 'cabbage', 'capsicum',
            'carrot', 'cauliflower', 'celery', 'chilli', 'cucumber',
            'garlic', 'kharif-onion-pyaz', 'lettuce', 'long-melon',
            'mushroom', 'okra', 'peas', 'potato', 'pumpkin',
            'rabi-onion-pyaz', 'radish', 'spinach', 'sponge-gourd',
            'squash-melon', 'summer-squash', 'sweet-potato', 'tomato', 'turnip'
        ]
    }
}

class ApniKhetiScraper:
    def __init__(self, use_selenium=True, headless=True):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
        self.use_selenium = use_selenium
        self.driver = None
        
        if use_selenium:
            self.setup_selenium(headless)
        
        self.scraped_data = []
        self.serial_number = 1
        
    def setup_selenium(self, headless=True):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            self.use_selenium = False
            
    def build_crop_url(self, section: str, category: str, crop_name: str) -> str:
        """Build the URL for a specific crop"""
        if section == 'agriculture':
            return f"https://www.apnikheti.com/en/pn/agriculture/crops/{category}/{crop_name}"
        else:  # horticulture
            return f"https://www.apnikheti.com/en/pn/agriculture/horticulture/{category}/{crop_name}"
    
    def click_show_more_buttons(self):
        """Click all 'Show More' buttons to expand content"""
        try:
            time.sleep(3)
            
            for attempt in range(3):
                logger.info(f"Attempt {attempt + 1} to find Show More buttons")
                
                selectors = [
                    "//button[contains(text(), 'Show More')]",
                    "//a[contains(text(), 'Show More')]",
                    "//*[contains(@class, 'show-more')]",
                    "//*[contains(text(), '+ Show More')]",
                    "//span[contains(text(), 'Show More')]",
                    "//*[@class='btn btn-link' and contains(text(), 'Show More')]"
                ]
                
                buttons_found = 0
                for selector in selectors:
                    try:
                        buttons = self.driver.find_elements(By.XPATH, selector)
                        
                        for i, button in enumerate(buttons):
                            try:
                                if button.is_displayed() and button.is_enabled():
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                    time.sleep(1)
                                    
                                    try:
                                        button.click()
                                        logger.info(f"Successfully clicked Show More button {i+1}")
                                    except:
                                        self.driver.execute_script("arguments[0].click();", button)
                                        logger.info(f"Successfully clicked Show More button {i+1} via JavaScript")
                                    
                                    buttons_found += 1
                                    time.sleep(2)
                                    
                            except Exception as e:
                                continue
                                
                    except Exception as e:
                        continue
                
                if attempt < 2:
                    time.sleep(3)
            
            time.sleep(5)
            logger.info("Completed Show More button clicking")
                    
        except Exception as e:
            logger.error(f"Error in click_show_more_buttons: {e}")
    
    def extract_section_content(self, soup: BeautifulSoup, section_keywords: List[str]) -> str:
        """Extract content from specific sections with better logic"""
        content_parts = []
        
        # Method 1: Look for specific section headers
        for keyword in section_keywords:
            headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'p'], 
                                   string=re.compile(keyword, re.IGNORECASE))
            
            for header in headers:
                content_elements = []
                current = header.find_next_sibling()
                
                for _ in range(5):
                    if current is None:
                        break
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    if current.name in ['p', 'div', 'span', 'li', 'td']:
                        text = current.get_text(strip=True)
                        if text and len(text) > 10:
                            content_elements.append(text)
                    current = current.find_next_sibling()
                
                if content_elements:
                    section_content = ' '.join(content_elements)
                    content_parts.append(section_content)
                    break
        
        # Method 2: Search in paragraphs if no structured content found
        if not content_parts:
            all_paragraphs = soup.find_all(['p', 'div'], string=re.compile('|'.join(section_keywords), re.IGNORECASE))
            for para in all_paragraphs[:3]:
                text = para.get_text(strip=True)
                if text and len(text) > 20:
                    content_parts.append(text)
        
        # Method 3: Search in all text as fallback
        if not content_parts:
            full_text = soup.get_text()
            for keyword in section_keywords:
                pattern = rf'(?i).*{re.escape(keyword)}.*?(?=\n\n|\.|$)'
                matches = re.findall(pattern, full_text)
                if matches:
                    content_parts.extend(matches[:2])
                    break
        
        # Clean and combine content
        final_content = ' | '.join(content_parts) if content_parts else "Data not available"
        
        # Clean the content
        final_content = re.sub(r'\s+', ' ', final_content)
        final_content = re.sub(r'Show More|Show Less', '', final_content)
        final_content = final_content.strip()
        
        return final_content if final_content else "Data not available"
    
    def scrape_crop_page(self, url: str, crop_name: str, category: str) -> Dict:
        """Scrape individual crop page with comprehensive data extraction"""
        try:
            logger.info(f"Scraping: {url}")
            
            if self.use_selenium and self.driver:
                self.driver.get(url)
                
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                self.click_show_more_buttons()
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                full_text = soup.get_text()
                
            else:
                response = self.session.get(url, timeout=15)
                if response.status_code != 200:
                    logger.warning(f"HTTP {response.status_code} for {url}")
                    return self.create_empty_record(crop_name, category, url)
                soup = BeautifulSoup(response.content, 'html.parser')
                full_text = soup.get_text()
            
            # Create crop data record with new headers
            crop_data = {
                'Serial Number': self.serial_number,
                'Category': category.replace('-', ' ').title(),
                'Variety': crop_name.replace('-', ' ').title(),
                'General Information': self.extract_section_content(soup, ['general', 'introduction', 'overview', 'about']),
                'Climate': self.extract_section_content(soup, ['climate', 'temperature', 'rainfall', 'weather', 'season']),
                'Soil': self.extract_section_content(soup, ['soil', 'ph', 'drainage', 'texture', 'fertility']),
                'Popular Varieties With Their Yield': self.extract_section_content(soup, ['varieties', 'cultivars', 'yield', 'production', 'qtl/acre']),
                'Land Preparation': self.extract_section_content(soup, ['land preparation', 'field preparation', 'tillage', 'ploughing']),
                'Sowing': self.extract_section_content(soup, ['sowing', 'planting', 'seeding', 'transplanting']),
                'Seed': self.extract_section_content(soup, ['seed', 'seed rate', 'seed treatment', 'germination']),
                'Fertilizer': self.extract_fertilizer_content(soup, full_text),
                'Weed Control': self.extract_section_content(soup, ['weed', 'herbicide', 'weeding', 'weed control']),
                'Irrigation': self.extract_section_content(soup, ['irrigation', 'water', 'moisture', 'watering']),
                'Plant Protection': self.extract_section_content(soup, ['plant protection', 'protection', 'spray', 'application']),
                'Diseases And Their Control': self.extract_section_content(soup, ['disease', 'pathogen', 'fungal', 'bacterial', 'viral', 'control']),
                'Harvesting': self.extract_section_content(soup, ['harvest', 'maturity', 'cutting', 'picking']),
                'Post-Harvest': self.extract_section_content(soup, ['post harvest', 'storage', 'processing', 'drying', 'packaging']),
                'References': url
            }
            
            self.serial_number += 1
            return crop_data
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return self.create_empty_record(crop_name, category, url)
    
    def create_empty_record(self, crop_name: str, category: str, url: str) -> Dict:
        """Create empty record for failed scrapes"""
        record = {
            'Serial Number': self.serial_number,
            'Category': category.replace('-', ' ').title(),
            'Variety': crop_name.replace('-', ' ').title(),
            'General Information': 'Data not available',
            'Climate': 'Data not available',
            'Soil': 'Data not available',
            'Popular Varieties With Their Yield': 'Data not available',
            'Land Preparation': 'Data not available',
            'Sowing': 'Data not available',
            'Seed': 'Data not available',
            'Fertilizer': 'Data not available',
            'Weed Control': 'Data not available',
            'Irrigation': 'Data not available',
            'Plant Protection': 'Data not available',
            'Diseases And Their Control': 'Data not available',
            'Harvesting': 'Data not available',
            'Post-Harvest': 'Data not available',
            'References': url
        }
        self.serial_number += 1
        return record
    
    def extract_fertilizer_content(self, soup: BeautifulSoup, full_text: str) -> str:
        """Extract comprehensive fertilizer information"""
        fertilizer_content = []
        
        # Look for fertilizer sections
        fertilizer_keywords = ['fertilizer', 'manure', 'nutrition', 'npk', 'urea', 'dap', 'ssp', 'mop']
        fertilizer_sections = self.extract_section_content(soup, fertilizer_keywords)
        
        if fertilizer_sections != "Data not available":
            fertilizer_content.append(fertilizer_sections)
        
        # Extract specific fertilizer dosages
        fertilizer_patterns = [
            (r'UREA\s*[:\-@]?\s*(\d+(?:\.\d+)?)\s*kg[/\s]*(?:acre|ha)', 'UREA'),
            (r'SSP\s*[:\-@]?\s*(\d+(?:\.\d+)?)\s*kg[/\s]*(?:acre|ha)', 'SSP'),
            (r'DAP\s*[:\-@]?\s*(\d+(?:\.\d+)?)\s*kg[/\s]*(?:acre|ha)', 'DAP'),
            (r'MOP\s*[:\-@]?\s*(\d+(?:\.\d+)?)\s*kg[/\s]*(?:acre|ha)', 'MOP'),
            (r'MURIATE\s+OF\s+POTASH\s*[:\-@]?\s*(\d+(?:\.\d+)?)\s*kg[/\s]*(?:acre|ha)', 'MURIATE OF POTASH')
        ]
        
        dosage_info = []
        for pattern, fert_name in fertilizer_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches:
                dosage_info.append(f"{fert_name}: {match} kg/acre")
        
        if dosage_info:
            fertilizer_content.append(f"Dosages: {'; '.join(dosage_info)}")
        
        # Look for NPK ratios
        npk_pattern = r'N:P:K\s*[:\-@]?\s*(\d+):(\d+):(\d+)'
        npk_matches = re.findall(npk_pattern, full_text, re.IGNORECASE)
        for match in npk_matches:
            fertilizer_content.append(f"NPK Ratio: {match[0]}:{match[1]}:{match[2]}")
        
        return ' | '.join(fertilizer_content) if fertilizer_content else "Data not available"
    
    def scrape_all_crops(self):
        """Scrape all crops from both sections"""
        logger.info("Starting comprehensive crop data scraping...")
        
        total_crops = sum(len(crops) for section in CROP_CATEGORIES.values() 
                         for crops in section.values())
        current_crop = 0
        successful_scrapes = 0
        
        for section_name, categories in CROP_CATEGORIES.items():
            logger.info(f"Scraping {section_name} section...")
            
            for category_name, crops in categories.items():
                logger.info(f"Processing {category_name} category...")
                
                for crop_name in crops:
                    current_crop += 1
                    logger.info(f"[{current_crop}/{total_crops}] Scraping {crop_name}...")
                    
                    url = self.build_crop_url(section_name, category_name, crop_name)
                    crop_data = self.scrape_crop_page(url, crop_name, category_name)
                    
                    if crop_data:
                        self.scraped_data.append(crop_data)
                        if crop_data['General Information'] != 'Data not available':
                            successful_scrapes += 1
                            logger.info(f"✓ Successfully scraped {crop_name}")
                        else:
                            logger.warning(f"⚠ Partial data for {crop_name}")
                    
                    # Delay between requests for stability
                    time.sleep(5)
        
        logger.info(f"Completed scraping. Total records: {len(self.scraped_data)}")
        logger.info(f"Successful scrapes: {successful_scrapes}/{total_crops}")
        
    def save_to_csv(self, filename='india_crop_dataset_complete.csv'):
        """Save scraped data to CSV file with specified headers"""
        if not self.scraped_data:
            logger.warning("No data to save!")
            return
            
        # Define the exact fieldnames as requested
        fieldnames = [
            'Serial Number',
            'Category', 
            'Variety',
            'General Information',
            'Climate',
            'Soil',
            'Popular Varieties With Their Yield',
            'Land Preparation',
            'Sowing',
            'Seed',
            'Fertilizer',
            'Weed Control',
            'Irrigation',
            'Plant Protection',
            'Diseases And Their Control',
            'Harvesting',
            'Post-Harvest',
            'References'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in self.scraped_data:
                    # Clean data
                    complete_row = {}
                    for field in fieldnames:
                        value = row.get(field, '')
                        if isinstance(value, str):
                            value = value.strip().replace('\n', ' ').replace('\r', '')
                            value = re.sub(r'\s+', ' ', value)
                            value = re.sub(r'Show\s*More|Show\s*Less', '', value)
                            value = value.strip()
                        complete_row[field] = value
                    writer.writerow(complete_row)
                    
            logger.info(f"Data saved to {filename}")
            
            # Print summary statistics
            logger.info(f"Total records saved: {len(self.scraped_data)}")
            categories = set(row.get('Category', '') for row in self.scraped_data)
            logger.info(f"Categories covered: {', '.join(sorted(categories))}")
            
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
    
    def save_sample_json(self, filename='sample_crop_data.json', sample_size=10):
        """Save a sample of scraped data in JSON format for inspection"""
        if not self.scraped_data:
            return
            
        sample_data = self.scraped_data[:sample_size]
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(sample_data, jsonfile, indent=2, ensure_ascii=False)
            logger.info(f"Sample data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving sample JSON: {e}")
            
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main execution function"""
    logger.info("Starting ApniKheti.com Complete Agricultural Data Scraper")
    logger.info("=" * 70)
    
    # Initialize scraper with headless mode for faster execution
    scraper = ApniKhetiScraper(use_selenium=True, headless=True)
    
    try:
        # Scrape all crop data
        scraper.scrape_all_crops()
        
        # Save to CSV with specified headers
        scraper.save_to_csv('india_crop_dataset_complete.csv')
        
        # Save sample JSON for inspection
        scraper.save_sample_json('sample_crop_data.json', 10)
        
        # Print detailed summary
        logger.info("=" * 70)
        logger.info(f"SCRAPING COMPLETED SUCCESSFULLY!")
        logger.info(f"Total records: {len(scraper.scraped_data)}")
        
        # Show sample of data structure
        if scraper.scraped_data:
            print("\nSample of scraped data structure:")
            sample = scraper.scraped_data[0]
            for key, value in sample.items():
                display_value = str(value)[:100] + "..." if len(str(value)) > 100 else value
                print(f"{key}: {display_value}")
                        
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()