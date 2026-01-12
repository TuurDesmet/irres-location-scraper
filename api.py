"""
Flask API for IRRES Location Scraper
Provides REST endpoints to fetch locations from IRRES.be
"""

from flask import Flask, jsonify, request
from scraper import IRRESLocationScraper, get_irres_locations, get_irres_office_images
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    API documentation endpoint.
    
    Returns:
        JSON with API information
    """
    return jsonify({
        "name": "IRRES Scraper API",
        "version": "1.0.0",
        "description": "Extracts property data from IRRES.be",
        "endpoints": {
            "GET /api/locations": "Fetch all available property locations",
            "GET /api/office-images": "Fetch IRRES office images",
            "GET /api/health": "Check API health status"
        }
    }), 200


@app.route('/api/locations', methods=['GET'])
def get_locations():
    """
    Get all available property locations from IRRES.be.
    
    Query Parameters:
        - format: Output format (json, csv) - default: json
    
    Returns:
        JSON response with locations list
    """
    try:
        logger.info("Fetching locations from IRRES.be")
        
        # Get locations
        result = get_irres_locations()
        
        # Check output format
        output_format = request.args.get('format', 'json').lower()
        
        if output_format == 'csv':
            return format_csv_response(result['locations'])
        
        # Default JSON format
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "locations": result['locations'],
                "count": len(result['locations'])
            }
        }
        
        logger.info(f"Successfully retrieved {len(result['locations'])} locations")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": str(e)
        }), 500


@app.route('/api/office-images', methods=['GET'])
def get_office_images():
    """
    Get IRRES office images from the contact page.
    
    Returns:
        JSON response with office images
    """
    try:
        logger.info("Fetching office images from IRRES.be")
        
        # Get office images
        result = get_irres_office_images()
        
        response = {
            "status": result['status'],
            "timestamp": datetime.now().isoformat(),
            "data": result['images']
        }
        
        if result['status'] == 'success':
            logger.info(f"Successfully retrieved {result['count']} office images")
            return jsonify(response), 200
        else:
            return jsonify(response), 500
        
    except Exception as e:
        logger.error(f"Error fetching office images: {str(e)}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "message": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON with API status
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "IRRES Location Scraper"
    }), 200


def format_csv_response(locations):
    """
    Format locations as CSV.
    
    Args:
        locations: List of location strings
        
    Returns:
        CSV formatted response
    """
    csv_content = "location\n"
    csv_content += "\n".join(locations)
    
    return app.response_class(
        response=csv_content,
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=irres_locations.csv"}
    )


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "message": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({
        "status": "error",
        "message": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
