# MyNewsRobot - Quick Reference

## 🚀 Common Commands

### Local Development

```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Run application
python src/main.py

# Run with different port
$env:PORT="8081"; python src/main.py

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### API Testing

```powershell
# Health check
curl http://localhost:8080/health

# Get configuration status
curl http://localhost:8080/config/status

# Trigger workflow (test mode)
curl -X POST http://localhost:8080/run `
  -H "Content-Type: application/json" `
  -d '{\"test_mode\": true}'

# Get root info
curl http://localhost:8080/
```

### Google Cloud

```powershell
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com run.googleapis.com

# Build image
gcloud builds submit --tag gcr.io/$PROJECT_ID/mynewsrobot

# Deploy to Cloud Run (Phase 5)
gcloud run deploy mynewsrobot \
  --image gcr.io/$PROJECT_ID/mynewsrobot \
  --platform managed \
  --region us-central1
```

## 📁 File Locations

### Configuration

-   **News Sources:** `config/news_sources.yaml`
-   **Topics:** `config/topic_priorities.yaml`
-   **Bookmarks:** `config/weekly_bookmarks.yaml`
-   **WordPress:** `config/wordpress.yaml`
-   **Style:** `config/writing_style.yaml`
-   **Environment:** `.env`

### Source Code

-   **Main App:** `src/main.py`
-   **Utilities:** `src/utils/`
    -   Config: `config_loader.py`
    -   Dates: `date_formatter.py`
    -   Memory: `memory_manager.py`
-   **Agents:** `src/agents/` (Phase 3)
-   **Tools:** `src/tools/` (Phase 2)
-   **Workflow:** `src/workflow/` (Phase 4)

### Documentation

-   **Setup:** `docs/setup.md`
-   **README:** `README.md`
-   **Project Plan:** `PROJECT_PLAN.md`
-   **Phase 1 Summary:** `PHASE1_SUMMARY.md`

## 🔧 Configuration Snippets

### Adding News Source (RSS)

```yaml
# config/news_sources.yaml
news_sources:
    your_category:
        pages:
            - url: "https://example.com/feed/"
              name: "Example Site"
              type: "rss"
```

### Adding Topic Priority

```yaml
# config/topic_priorities.yaml
topics:
    - name: "Your Topic"
      keywords: ["keyword1", "keyword2"]
      priority: 9
```

### Adding Weekly Bookmark

```yaml
# config/weekly_bookmarks.yaml
bookmarks:
    - url: "https://example.com/article"
      note: "Important read"
      submitted_date: "2025-11-28"
```

## 🐛 Troubleshooting

### Port Already in Use

```powershell
# Change port
$env:PORT="8081"
python src/main.py
```

### Import Errors

```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Config Not Loading

```python
# Test config loader
python -c "from src.utils.config_loader import config_loader; print(config_loader.get_news_sources())"
```

### Google Cloud Auth

```powershell
# Re-authenticate
gcloud auth application-default login
```

## 📊 Phase Checklist

### Phase 1 ✅

-   [x] Project structure
-   [x] Dependencies
-   [x] Configuration system
-   [x] Gemini connection setup
-   [x] Memory service
-   [x] FastAPI app
-   [x] Documentation

### Phase 2 ✅

-   [x] WebScraperTool
-   [x] BookmarkLoaderTool
-   [x] WordPressTool
-   [x] Unit tests for tools

### Phase 3

-   [ ] NewsResearchAgent
-   [ ] ContentExtractionAgent
-   [ ] ContentAnalysisAgent
-   [ ] ContentWritingAgent
-   [ ] Integration tests

### Phase 4

-   [ ] SequentialAgent orchestration
-   [ ] PublishingAgent
-   [ ] End-to-end workflow testing

### Phase 5

-   [ ] Datadog integration
-   [ ] Cloud Run deployment
-   [ ] Cloud Scheduler setup
-   [ ] Production testing

### Phase 6

-   [ ] ImagenTool
-   [ ] ImageGenerationAgent
-   [ ] Image integration

## 🔑 Environment Variables

```env
# Required
GOOGLE_API_KEY=your-google-ai-studio-api-key
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Optional: Google Cloud (only for Cloud Run deployment)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Datadog
DD_API_KEY=your-datadog-key
DD_SITE=datadoghq.com
PORT=8080
LOG_LEVEL=INFO
DEVELOPMENT_MODE=true
```

## 📝 Quick Notes

**Topic Priority Scale:**

-   11 = User bookmarks (automatic)
-   10 = Must-have
-   9 = Very interested
-   8 = Interested
-   7 = Nice to have

**Summary Guidelines:**

-   Each item: ~200 tokens (~150 words)
-   Total: 20 items per week
-   Always include source link
-   Write in personal style

**RSS vs HTML:**

-   RSS feeds preferred (faster, structured)
-   Tool auto-detects format
-   Type field optional in config

## 🆘 Getting Help

-   **ADK Docs:** https://google.github.io/adk-docs/
-   **FastAPI:** https://fastapi.tiangolo.com/
-   **WordPress API:** https://developer.wordpress.org/rest-api/
-   **Project Plan:** `PROJECT_PLAN.md`
-   **Setup Guide:** `docs/setup.md`

---

**Current Phase:** 2 ✅ | **Next Phase:** 3 (Agent Development)
