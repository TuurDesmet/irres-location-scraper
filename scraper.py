"""
IRRES Location Scraper Module
Extracts available locations from IRRES.be property listings.
Handles UTF-8 character normalization automatically.
"""

import requests
from bs4 import BeautifulSoup
import unicodedata
from typing import List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IRRESLocationScraper:
    """
    Scraper for extracting property locations from IRRES.be
    """
    
    BASE_URL = "https://irres.be/te-koop"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
        self.locations = []
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize UTF-8 text to remove accents and special characters.
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text string
        """
        # Decompose unicode characters
        nfd = unicodedata.normalize('NFD', text)
        # Remove combining characters (accents, diacritics)
        result = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
        return result
    
    def fetch_page(self) -> str:
        """
        Fetch the IRRES.be property listing page.
        
        Returns:
            HTML content of the page
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            logger.info(f"Fetching page: {self.BASE_URL}")
            response = requests.get(
                self.BASE_URL,
                headers=self.HEADERS,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page: {e}")
            raise
    
    def parse_locations(self, html: str) -> List[str]:
        """
        Parse locations from HTML content.
        Extracts location labels from data attributes.
        
        Args:
            html: HTML content to parse
            
        Returns:
            List of unique locations
        """
        soup = BeautifulSoup(html, 'html.parser')
        locations_set = set()
        
        # Known non-location labels to exclude
        excluded_labels = {
            'appartement', 'huis', 'grond', 'contact',
            'droomwoning', 'nieuwbouw', 'verkocht', 'verkopen',
            'te-koop', 'aanbod', 'rekrutering'
        }
        
        # Find all elements with data-label attribute
        elements = soup.find_all(attrs={"data-label": True})
        
        for element in elements:
            label = element.get('data-label', '').strip()
            
            # Filter out non-location labels
            if (label and 
                label.lower() not in excluded_labels and
                '€' not in label and
                not any(char.isdigit() for char in label)):
                locations_set.add(label)
        
        # Convert to sorted list
        locations = sorted(list(locations_set))
        logger.info(f"Found {len(locations)} unique locations")
        
        return locations
    
    def scrape(self) -> Dict[str, List[str]]:
        """
        Main scraping method. Fetches and parses locations.
        
        Returns:
            Dictionary with locations list
        """
        try:
            html = self.fetch_page()
            locations = self.parse_locations(html)
            self.locations = locations
            return {
                "locations": locations,
                "count": len(locations),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {
                "locations": [],
                "count": 0,
                "status": "error",
                "error": str(e)
            }
    
    def get_locations(self) -> List[str]:
        """
        Get the list of scraped locations.
        
        Returns:
            List of locations
        """
        return self.locations


def get_irres_locations() -> Dict[str, List[str]]:
    """
    Convenience function to fetch IRRES locations.
    
    Returns:
        Dictionary containing locations list
    """
    scraper = IRRESLocationScraper()
    return scraper.scrape()


class IRRESOfficeImagesScraper:
    """
    Scraper for extracting office images from IRRES.be contact page
    """
    
    BASE_URL = "https://irres.be/contact"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 10):
        """
        Initialize the scraper.
        
        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self.timeout = timeout
    
    def fetch_page(self) -> str:
        """
        Fetch the IRRES.be contact page.
        
        Returns:
            HTML content of the page
            
        Raises:
            requests.RequestException: If the request fails
        """
        try:
            logger.info(f"Fetching page: {self.BASE_URL}")
            response = requests.get(
                self.BASE_URL,
                headers=self.HEADERS,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch page: {e}")
            raise
    
    def parse_office_images(self, html: str) -> Dict[str, str]:
        """
        Parse office images from HTML content.
        
        Args:
            html: HTML content to parse
            
        Returns:
            Dictionary with office images
        """
        soup = BeautifulSoup(html, 'html.parser')
        images = {}
        
        # Find all picture elements that contain the office images
        picture_elements = soup.find_all('picture')
        
        for picture in picture_elements:
            # Find img tags within picture elements
            img = picture.find('img')
            if not img:
                continue
            
            srcset = img.get('srcset', '')
            alt = img.get('alt', '').lower()
            
            # Extract the first URL from srcset
            if srcset:
                url = srcset.split()[0].lstrip('/')
                
                # Identify which office based on the URL or alt text
                if '7723384' in url or 'kerstgevel' in url or 'latem' in alt:
                    images['IrresLatemImage'] = f"https://irres.be/{url}"
                elif '7723383' in url or 'destelbergen' in url:
                    images['IrresDestelbergenImage'] = f"https://irres.be/{url}"
        
        logger.info(f"Found {len(images)} office images")
        return images
    
    def scrape(self) -> Dict[str, any]:
        """
        Main scraping method. Fetches and parses office images.
        
        Returns:
            Dictionary with office images and metadata
        """
        try:
            html = self.fetch_page()
            images = self.parse_office_images(html)
            
            return {
                "status": "success",
                "images": images,
                "count": len(images)
            }
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {
                "status": "error",
                "images": {},
                "count": 0,
                "error": str(e)
            }


def get_irres_office_images() -> Dict[str, any]:
    """
    Convenience function to fetch IRRES office images.
    
    Returns:
        Dictionary with office images
    """
    scraper = IRRESOfficeImagesScraper()
    return scraper.scrape()


if __name__ == "__main__":
    # Example usage
    print("=== Locations ===")
    scraper = IRRESLocationScraper()
    result = scraper.scrape()
    
    print(f"Status: {result['status']}")
    print(f"Total locations found: {result['count']}")
    print("\nLocations:")
    for location in result['locations']:
        print(f"  - {location}")
    
    print("\n=== Office Images ===")
    image_scraper = IRRESOfficeImagesScraper()
    image_result = image_scraper.scrape()
    
    print(f"Status: {image_result['status']}")
    print(f"Office images found: {image_result['count']}")
    print("\nImages:")
    for key, url in image_result['images'].items():
        print(f"  {key}: {url}")
