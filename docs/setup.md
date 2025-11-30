# MyNewsRobot - Setup Guide

## Prerequisites

-   **Python 3.13+** (required for Cloud Run compatibility)
-   **Google Cloud Project** with billing enabled
-   **WordPress Site** with REST API access
-   **Git** for version control
-   **(Optional) Datadog Account** for observability

## Step-by-Step Setup

### 1. Clone and Install Dependencies

```powershell
# Navigate to workspace
cd c:\workspace\mynewsrobot

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import google.adk; print('ADK installed successfully')"
```

### 2. Configure Google Cloud

```powershell
# Install Google Cloud SDK if not already installed
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable \
    aiplatform.googleapis.com \
    run.googleapis.com \
    cloudscheduler.googleapis.com \
    cloudbuild.googleapis.com
```

### 3. Set Up Environment Variables

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your actual values
notepad .env
```

Required environment variables:

```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# WordPress
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Datadog (optional for Phase 1-4)
DD_API_KEY=your-datadog-api-key
DD_SITE=datadoghq.com
```

### 4. Configure WordPress Access

#### Create Application Password:

1. Log into your WordPress admin panel
2. Go to **Users** → **Profile**
3. Scroll to **Application Passwords**
4. Enter name: "MyNewsRobot"
5. Click **Add New Application Password**
6. Copy the generated password
7. Add to `.env` as `WORDPRESS_APP_PASSWORD`

#### Update WordPress Config:

Edit `config/wordpress.yaml`:

```yaml
wordpress:
    site_url: "https://your-site.com" # Your actual WordPress URL
    api_endpoint: "/wp-json/wp/v2"
```

### 5. Configure News Sources

Edit `config/news_sources.yaml` with your preferred sources:

```yaml
news_sources:
    tech:
        pages:
            - url: "https://arstechnica.com/feed/"
              name: "Ars Technica"
              type: "rss"
            # Add your sources here
```

**Finding RSS Feeds:**

-   Look for RSS icon on websites
-   Try adding `/feed/` or `/rss/` to the URL
-   Use browser extensions like "RSS Feed Reader"
-   Check `<link rel="alternate" type="application/rss+xml">` in page source

### 6. Set Topic Priorities

Edit `config/topic_priorities.yaml`:

```yaml
topics:
    - name: "AI/Machine Learning"
      keywords: ["AI", "LLM", "GPT", "machine learning"]
      priority: 10 # Your highest interest

    - name: "Your Topic Here"
      keywords: ["keyword1", "keyword2"]
      priority: 8
```

Priority scale:

-   **10**: Must-have topics
-   **9**: Very interested
-   **8**: Interested
-   **7**: Nice to have
-   **11**: Reserved for user bookmarks (automatic)

### 7. Test Local Setup

```powershell
# Run the application
python src/main.py
```

Open another terminal and test:

```powershell
# Health check
curl http://localhost:8080/health

# Configuration status
curl http://localhost:8080/config/status

# Trigger workflow (test mode)
curl -X POST http://localhost:8080/run `
  -H "Content-Type: application/json" `
  -d '{\"test_mode\": true}'
```

Expected output:

```json
{
    "status": "success",
    "message": "Workflow completed successfully (Phase 1 - configuration only)",
    "execution_time": 0.05,
    "articles_found": 0,
    "summary_url": ""
}
```

### 8. Run Tests

```powershell
# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

## Configuration Files Reference

| File                           | Purpose                           | Required |
| ------------------------------ | --------------------------------- | -------- |
| `.env`                         | Environment variables and secrets | Yes      |
| `config/news_sources.yaml`     | RSS feeds and pages to monitor    | Yes      |
| `config/topic_priorities.yaml` | Interest rankings                 | Yes      |
| `config/weekly_bookmarks.yaml` | Your weekly bookmarks             | No       |
| `config/wordpress.yaml`        | WordPress site settings           | Yes      |
| `config/writing_style.yaml`    | Style guidelines for LLM          | Yes      |

## Troubleshooting

### Import Errors

```powershell
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Google Cloud Authentication

```powershell
# Re-authenticate
gcloud auth application-default login

# Verify credentials
gcloud auth application-default print-access-token
```

### Configuration Not Loading

```python
# Test configuration loader
python -c "from src.utils.config_loader import config_loader; print(config_loader.get_news_sources())"
```

### Port Already in Use

```powershell
# Change port in .env
PORT=8081

# Or specify when running
$env:PORT="8081"; python src/main.py
```

## Next Steps

✅ **Phase 1 Complete!** You now have:

-   ✅ Project structure with all dependencies
-   ✅ Configuration system
-   ✅ Basic memory management
-   ✅ FastAPI application with health checks
-   ✅ Development environment ready

🔄 **Ready for Phase 2:** Building custom tools

-   WebScraperTool (RSS + HTML)
-   BookmarkLoaderTool
-   WordPressTool

## Getting Help

-   **Google ADK Docs**: https://google.github.io/adk-docs/
-   **FastAPI Docs**: https://fastapi.tiangolo.com/
-   **WordPress REST API**: https://developer.wordpress.org/rest-api/

---

**Questions?** Review the `PROJECT_PLAN.md` for detailed architecture and implementation phases.
