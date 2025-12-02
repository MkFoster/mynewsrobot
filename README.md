# MyNewsRobot

An intelligent AI agent system that creates personalized weekly news summaries and publishes them to WordPress. Built with Google's Agent Development Kit (ADK), it aggregates content from RSS feeds, analyzes and prioritizes articles based on user-defined topics, and generates summaries in a consistent style.

## 🎯 Features

-   **RSS Feed Aggregation** - Discovers articles from 100+ RSS feeds across multiple categories
-   **Smart Prioritization** - Ranks content based on topic priorities and personal bookmarks
-   **AI-Powered Writing** - Generates summaries in your writing style using Gemini 2.5 Flash
-   **WordPress Publishing** - Automatically posts private newsletters for review
-   **Multi-Agent Architecture** - 3 specialized agents working in sequence
-   **Topic Diversity** - Ensures balanced content across interests (max 10 per topic)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MyNewsRobot Workflow                     │
├─────────────────────────────────────────────────────────────┤
│  📰 Discovery → 🔍 Analysis → ✍️ Writing → 🚀 Publishing    │
└─────────────────────────────────────────────────────────────┘
```

**3-Agent Sequential Workflow:**

1. **ContentAnalysisAgent** - Selects top 20 articles based on topic priorities
2. **ContentWritingAgent** - Generates personalized summaries (~150 words each)
3. **PublishingAgent** - Publishes to WordPress as private post

See [Architecture.md](Architecture.md) for detailed documentation.

## 🚀 Quick Start

### Prerequisites

-   Python 3.14+
-   Google AI Studio API key ([get one here](https://makersuite.google.com/app/apikey))
-   WordPress site with Application Password authentication
-   Virtual environment (recommended)

### Installation

```powershell
# Clone the repository
git clone https://github.com/MkFoster/mynewsrobot.git
cd mynewsrobot

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Create `.env` file** with your credentials:

```env
# Required
GOOGLE_API_KEY=your-google-ai-studio-api-key
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Optional
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
PORT=8080
LOG_LEVEL=INFO
```

2. **Configure your preferences** in `config/`:
    - `news_sources.yaml` - RSS feed URLs by category
    - `topic_priorities.yaml` - Topics with priority scores (7-11)
    - `weekly_bookmarks.yaml` - Manually curated articles
    - `writing_style.yaml` - Writing style guidelines
    - `wordpress_config.yaml` - WordPress site settings

### Running Locally

```powershell
# Activate virtual environment (if not already)
.\venv\Scripts\activate

# Start the FastAPI server
python src/main.py

# Server runs on http://localhost:8080
```

**Trigger the workflow:**

```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://localhost:8080/run" -Method POST -ContentType "application/json" -Body '{"newsletter_date": "December 1, 2025"}'

# Using curl
curl -X POST http://localhost:8080/run -H "Content-Type: application/json" -d "{\"newsletter_date\": \"December 1, 2025\"}"
```

**Check configuration status:**

```powershell
curl http://localhost:8080/config/status
```

**Health check:**

```powershell
curl http://localhost:8080/health
```

## 📁 Project Structure

```
mynewsrobot/
├── config/                      # Configuration files
│   ├── news_sources.yaml       # RSS feed URLs
│   ├── topic_priorities.yaml   # Topics with priority scores
│   ├── weekly_bookmarks.yaml   # User-curated articles
│   ├── writing_style.yaml      # Style guidelines
│   └── wordpress_config.yaml   # WordPress settings
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/                 # Agent implementations
│   │   ├── content_analysis_agent.py
│   │   ├── content_writing_agent.py
│   │   └── publishing_agent.py
│   ├── tools/                  # Custom tools
│   │   ├── news_scraper.py    # RSS feed aggregator
│   │   ├── topic_priorities_tool.py
│   │   └── wordpress_tool.py  # WordPress API client
│   └── utils/                  # Utility modules
│       ├── config_loader.py
│       ├── date_formatter.py
│       └── session_service.py
├── tests/                      # Test suite (62 tests)
├── .env                        # Environment variables (create this)
├── requirements.txt            # Python dependencies
├── Architecture.md             # Detailed architecture docs
├── Requirements.md             # Feature requirements
└── README.md                   # This file
```

## 🧪 Testing

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py -v
```

## 🔧 Configuration Guide

### Adding RSS Feeds

Edit `config/news_sources.yaml`:

```yaml
news_sources:
    tech:
        pages:
            - url: "https://example.com/feed/"
              name: "Example Tech Blog"
              type: "rss"
```

### Setting Topic Priorities

Edit `config/topic_priorities.yaml`:

```yaml
topics:
    - name: "Artificial Intelligence"
      keywords: ["AI", "machine learning", "LLM", "GPT"]
      priority: 10 # Scale: 7-11 (11 = must-have)
```

### Adding Weekly Bookmarks

Edit `config/weekly_bookmarks.yaml`:

```yaml
bookmarks:
    - url: "https://example.com/important-article"
      note: "Key insights on AI agents"
      submitted_date: "2025-12-01"
```

Bookmarks automatically get priority 11 and are always included.

### WordPress Setup

1. **Generate Application Password:**

    - Log into WordPress
    - Go to Users → Profile
    - Scroll to "Application Passwords"
    - Create new password (spaces are automatically removed by the system)

2. **Configure settings** in `config/wordpress_config.yaml`:

```yaml
wordpress:
    site_url: "https://yoursite.com"
    default_category: "WeeklySummary"
    default_status: "private"
```

## 🔑 Environment Variables

| Variable                 | Required | Description                       |
| ------------------------ | -------- | --------------------------------- |
| `GOOGLE_API_KEY`         | Yes      | Google AI Studio API key          |
| `WORDPRESS_USERNAME`     | Yes      | WordPress username                |
| `WORDPRESS_APP_PASSWORD` | Yes      | WordPress Application Password    |
| `GOOGLE_CLOUD_PROJECT`   | No       | GCP project ID (for Cloud Run)    |
| `GOOGLE_CLOUD_LOCATION`  | No       | GCP region (default: us-central1) |
| `PORT`                   | No       | Server port (default: 8080)       |
| `LOG_LEVEL`              | No       | Logging level (default: INFO)     |

## 📊 Workflow Execution

When you trigger `/run`, here's what happens:

1. **Discovery** (~5-10s)

    - Fetches articles from all RSS feeds
    - Saves to `discovered_articles.json`
    - Typical output: 100+ articles

2. **Analysis** (~3-5s)

    - ContentAnalysisAgent loads topic priorities
    - Matches articles to topics by keywords
    - Selects top 20 (max 10 per topic)
    - Saves to `analyzed_articles.json`

3. **Writing** (~10-15s)

    - ContentWritingAgent generates summaries
    - ~150 words per article
    - Saves to `newsletter_draft.html`

4. **Publishing** (~2-3s)
    - PublishingAgent creates WordPress post
    - Status: Private
    - Category: WeeklySummary
    - Returns post URL

**Total Time:** ~20-30 seconds

## 🐛 Troubleshooting

### Port Already in Use

```powershell
$env:PORT="8081"
python src/main.py
```

### Import Errors

```powershell
pip install -r requirements.txt --force-reinstall
```

### WordPress 401 Errors

-   Verify Application Password is correct
-   Check user has Author/Editor/Admin role
-   Confirm WordPress REST API is enabled

### Agent Not Calling Tools

-   Check agent instructions are clear and explicit
-   Verify tools are in the tools array
-   Review logs for LLM response patterns

### Configuration Not Loading

```powershell
python -c "from src.utils.config_loader import config_loader; print(config_loader.get_news_sources())"
```

## 🚀 Deployment

### Google Cloud Run

```powershell
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com run.googleapis.com

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/mynewsrobot
gcloud run deploy mynewsrobot \
  --image gcr.io/$PROJECT_ID/mynewsrobot \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=...,WORDPRESS_USERNAME=...
```

### Cloud Scheduler (Weekly)

```powershell
gcloud scheduler jobs create http weekly-newsletter \
  --schedule="0 9 * * 1" \
  --uri=https://mynewsrobot-xxx.run.app/run \
  --http-method=POST \
  --message-body='{"newsletter_date":"current"}' \
  --time-zone="America/New_York"
```

## 📈 Performance

-   **Execution Time:** 20-30 seconds end-to-end
-   **Cost per Run:** ~$0.10 (Gemini 2.5 Flash)
-   **Monthly Cost:** <$5 for weekly execution
-   **RSS Feeds:** Handles 500+ feeds efficiently
-   **Token Usage:** ~50,000 tokens per run

## 🔮 Future Enhancements

-   **Image Generation** - AI-generated visuals using Imagen
-   **Web Admin Interface** - Manage sources and topics via UI
-   **Chrome Extension** - One-click bookmark submission
-   **Email Distribution** - Send via SendGrid/Mailgun
-   **Audio Podcast** - Spoken version using Google TTS
-   **Video Animations** - Google Veo for weekly themes

See [Requirements.md](Requirements.md) for full roadmap.

## 📚 Documentation

-   [Architecture.md](Architecture.md) - Detailed system architecture
-   [Requirements.md](Requirements.md) - Feature requirements and roadmap
-   [CapstoneInfo.md](CapstoneInfo.md) - Capstone project overview

## 🆘 Support

-   **Google ADK Docs:** https://google.github.io/adk-docs/
-   **FastAPI Docs:** https://fastapi.tiangolo.com/
-   **WordPress REST API:** https://developer.wordpress.org/rest-api/
-   **Application Passwords Guide:** https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/

## 📝 License

See [LICENSE](LICENSE) file.

## 👤 Author

Mark Foster

---

**Status:** ✅ Core Implementation Complete | **Version:** 0.1.0 | **Last Updated:** December 1, 2025
