# Deploying IRRES Location Scraper on Render

## Prerequisites

- GitHub account with your repository
- Render account (free at https://render.com)

## Step-by-Step Deployment Guide

### 1. Prepare Your Repository

Your repository already has the `render.yaml` configuration file. Make sure it's pushed to GitHub:

```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Connect GitHub to Render

1. Go to https://dashboard.render.com
2. Click **"New +"** button
3. Select **"Web Service"**
4. Click **"Connect account"** and authorize your GitHub
5. Select the repository: `irres-location-scraper`
6. Click **"Connect"**

### 3. Configure the Service

**Service Name:** `irres-location-scraper`

**Environment:** Python 3

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `gunicorn wsgi:app`

**Plan:** Free (or Starter for better performance)

### 4. Set Environment Variables

In the Render dashboard, add these environment variables:

```
FLASK_ENV = production
FLASK_DEBUG = False
REQUEST_TIMEOUT = 10
LOG_LEVEL = INFO
PORT = 10000
```

### 5. Deploy

1. Click **"Deploy"** button
2. Wait for the build to complete (2-3 minutes)
3. Your API will be available at: `https://irres-location-scraper.onrender.com`

## API Endpoints

Once deployed, access your API at:

- **GET /api/locations** - Get property locations
  ```bash
  curl https://irres-location-scraper.onrender.com/api/locations
  ```

- **GET /api/office-images** - Get office images
  ```bash
  curl https://irres-location-scraper.onrender.com/api/office-images
  ```

- **GET /api/health** - Health check
  ```bash
  curl https://irres-location-scraper.onrender.com/api/health
  ```

- **GET /** - API documentation
  ```bash
  curl https://irres-location-scraper.onrender.com/
  ```

## Important Notes

### Free Tier Limitations

- Service spins down after 15 minutes of inactivity
- Slower performance than paid plans
- Limited to 100GB outbound bandwidth per month

### Recommended for Production

- Upgrade to **Starter** plan ($7/month minimum)
- Enables:
  - Always-on service (no spin-down)
  - Better performance
  - More reliable uptime

### Monitoring

Monitor your deployment in the Render dashboard:
- Click on your service name
- View **Logs** tab for real-time output
- View **Events** tab for deployment history
- View **Metrics** tab for performance

## Troubleshooting

### Deployment Failed

Check the build logs:
1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. Scroll to see error messages

Common issues:
- Missing `requirements.txt` file
- Python version mismatch
- Syntax errors in Python code

### API Not Responding

1. Check if service is running (green status in dashboard)
2. Wait for service to spin up if using free tier
3. Check the **Logs** for errors

### Slow Response Times

- Free tier services are slower
- Upgrade to Starter plan for better performance
- First request may be slow if service is spinning up

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| FLASK_ENV | production | Flask environment |
| FLASK_DEBUG | False | Debug mode (must be False in production) |
| REQUEST_TIMEOUT | 10 | Scraper request timeout (seconds) |
| LOG_LEVEL | INFO | Logging level (INFO, DEBUG, WARNING, ERROR) |
| PORT | 10000 | Port Render assigns (automatic) |

## Updating Your API

After making changes to your code:

1. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update API"
   git push origin main
   ```

2. Render will automatically redeploy if you have "Auto-Deploy" enabled
   - Or manually click "Manual Deploy" in Render dashboard

## Custom Domain (Optional)

To use a custom domain:

1. In Render dashboard, go to your service
2. Click **"Settings"** tab
3. Scroll to **"Custom Domain"**
4. Enter your domain (e.g., `api.example.com`)
5. Add the DNS CNAME record provided by Render to your domain registrar

## Example cURL Commands

### Get Locations
```bash
curl https://irres-location-scraper.onrender.com/api/locations
```

### Get Office Images
```bash
curl https://irres-location-scraper.onrender.com/api/office-images
```

### Pretty Print JSON
```bash
curl https://irres-location-scraper.onrender.com/api/office-images | python -m json.tool
```

## Need Help?

- Render Documentation: https://render.com/docs
- Flask Documentation: https://flask.palletsprojects.com/
- Gunicorn Documentation: https://gunicorn.org/

