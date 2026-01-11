from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import uvicorn


app = FastAPI(
    title="Irres.be Location Scraper API",
    description="API to fetch available locations from irres.be property filter",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IrresLocationScraper:
    """
    Scraper for extracting available locations from irres.be property filter.
    """
    
    def __init__(self):
        self.base_url = "https://irres.be/te-koop"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def fetch_page(self) -> Optional[str]:
        """
        Fetch the HTML content of the page.
        
        Returns:
            HTML content as string or None if request fails
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_locations(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract location data from HTML content.
        
        Args:
            html_content: HTML string to parse
            
        Returns:
            List of dictionaries containing location information
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        locations = []
        
        # Find the ul element containing the locations
        location_ul = soup.find('ul', class_=lambda x: x and 'search-values' in x)
        
        if not location_ul:
            print("Could not find location filter element")
            return locations
        
        # Extract all li elements
        location_items = location_ul.find_all('li')
        
        for item in location_items:
            location_data = {
                'label': item.get('data-label', '').strip(),
                'value': item.get('data-value', '').strip(),
                'display_text': item.get_text(strip=True)
            }
            
            # Only add if we have valid data
            if location_data['label'] and location_data['value']:
                locations.append(location_data)
        
        return locations
    
    def get_locations(self) -> List[Dict[str, str]]:
        """
        Main method to fetch and extract all available locations.
        
        Returns:
            List of location dictionaries with label, value, and display_text
        """
        html_content = self.fetch_page()
        
        if not html_content:
            return []
        
        locations = self.extract_locations(html_content)
        return locations


# Initialize scraper
scraper = IrresLocationScraper()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Irres.be Location Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/locations": "Get all available locations",
            "/locations/labels": "Get only location labels",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/locations", response_model=List[Dict[str, str]])
async def get_locations():
    """
    Get all available locations from irres.be filter
    
    Returns:
        List of locations with label, value, and display_text
    """
    try:
        locations = scraper.get_locations()
        
        if not locations:
            raise HTTPException(
                status_code=404, 
                detail="No locations found or error fetching data"
            )
        
        return locations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/locations/labels", response_model=List[str])
async def get_location_labels():
    """
    Get only the location labels (display names)
    
    Returns:
        List of location label strings
    """
    try:
        locations = scraper.get_locations()
        
        if not locations:
            raise HTTPException(
                status_code=404, 
                detail="No locations found or error fetching data"
            )
        
        return [loc['label'] for loc in locations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/locations/count")
async def get_location_count():
    """
    Get the total count of available locations
    
    Returns:
        Dictionary with count
    """
    try:
        locations = scraper.get_locations()
        return {"count": len(locations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
