# MyNewsRobot - Project Plan

## Project Overview

A concierge agent that creates custom weekly news summaries/newsletters, posting them automatically to WordPress. Built with Google Agent Development Kit (ADK) and deployed on Google Cloud Platform.

## Technology Stack

### Core Framework

-   **Google ADK (Agent Development Kit)** - Multi-agent orchestration framework.
    Use Context7 MCP server to get update docs when neeeded.
    ADK Python code examples for agents can be found here: https://github.com/google/adk-python
-   **Python 3.13** - Latest stable Cloud Run base image support
-   **Gemini 2.5 Flash** - Primary LLM model (can upgrade to Pro if needed)

### Google Cloud Services

-   **Cloud Run Jobs** - Weekly execution environment
-   **Cloud Scheduler** - Weekly trigger (e.g., every Sunday at 6 AM)
-   **Vertex AI** - Gemini model hosting
-   **Cloud Build** - CI/CD for containerization
-   **Datadog** - Observability and monitoring

### External Integrations

-   **WordPress REST API** - Content publishing
-   **Imagen API** - Featured image generation (Phase 6)

## Architecture Design

### Multi-Agent Sequential Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    SequentialAgent                           │
│  (Orchestrates the entire weekly summary pipeline)          │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  1. NewsResearchAgent (LlmAgent)              │
    │  - Checks configured news site URLs           │
    │  - Processes user bookmark file               │
    │  - Uses WebScraperTool to get page content    │
    │  - Parses RSS feeds and HTML pages            │
    │  - Discovers articles from provided sources   │
    │  - Output: list of article URLs + metadata    │
    └───────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  2. ContentExtractionAgent (LlmAgent)         │
    │  - Uses custom WebScraperTool                 │
    │  - For RSS feeds: uses content tag summary    │
    │  - For HTML: fetches full article content     │
    │  - Extracts text, images, metadata            │
    │  - Output: enriched article data              │
    └───────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  3. ContentAnalysisAgent (LlmAgent)           │
    │  - Uses memory to check for duplicates        │
    │  - Applies topic priorities to rank articles  │
    │  - User bookmarks get priority 11 (highest)   │
    │  - Selects top 20 items for weekly summary    │
    │  - Output: ranked article list (20 items)     │
    └───────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  4. ContentWritingAgent (LlmAgent)            │
    │  - Trained on mkfoster.com style              │
    │  - Trained on fireflywp.com style             │
    │  - Writes summaries with citations            │
    │  - Each item summary: ~200 tokens max         │
    │  - Generates weekly title with date           │
    │  - Creates excerpt                            │
    │  - Output: formatted newsletter               │
    └───────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  5. PublishingAgent (LlmAgent)                │
    │  - Uses WordPressTool (custom)                │
    │  - Posts to WordPress as private              │
    │  - Adds "WeeklySummary" category              │
    │  - Output: WordPress post URL                 │
    └───────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────┐
    │  6. ImageGenerationAgent (Optional - Phase 6) │
    │  - Uses ImagenTool (custom)                   │
    │  - Generates featured image (3:2 ratio)       │
    │  - Creates images for select articles         │
    │  - Updates WordPress post with images         │
    │  - Output: image URLs and metadata            │
    └───────────────────────────────────────────────┘
```

### Custom Tools

#### 1. WebScraperTool

-   **Purpose**: Fetch and extract article content from URLs and RSS feeds
-   **Technology**: requests + BeautifulSoup4 / newspaper3k + feedparser
-   **Features**:
    -   Parse RSS/Atom feeds to discover article links
    -   Extract summaries from RSS content tags (when available)
    -   Extract HTML article content (title, content, author, date)
    -   Handles various article formats
    -   Extracts existing images from articles
    -   Error handling for paywalls/blocked content
    -   Supports both RSS feeds and direct HTML pages
    -   **Optimization**: For RSS feeds, use content tag for summaries instead of loading full articles

#### 2. WordPressTool

-   **Purpose**: Publish content to WordPress via REST API
-   **Features**:
    -   Authenticate with WordPress
    -   Create posts with HTML content
    -   Upload and attach images
    -   Set categories, tags, featured image
    -   Set post status to "private"
    -   Returns post URL

#### 3. BookmarkLoaderTool

-   **Purpose**: Load user-submitted bookmarks from weekly_bookmarks.yaml
-   **Features**:
    -   Read from config/weekly_bookmarks.yaml (or override path)
    -   Parse YAML format with URL, note, and date
    -   Validate URLs
    -   Automatically assign priority 11 (highest)
    -   Returns list of bookmark URLs with metadata

#### 4. ImagenTool (Phase 6 - Optional Enhancement)

-   **Purpose**: Generate AI images for newsletter
-   **Features**:
    -   Generate featured image based on weekly theme
    -   Generate article-specific images
    -   3:2 aspect ratio for featured images
    -   Returns image URLs and metadata
    -   Update existing WordPress posts with images

### Memory & Context Management

```python
# Using ADK InMemoryMemoryService for development
# Upgrade to Cloud-based memory for production

from google.adk.memory import InMemoryMemoryService

memory_config = {
    "service": InMemoryMemoryService(),
    "session_ttl": "7 days",  # Keep context for a week
    "deduplication": True,     # Avoid duplicate articles
}

# Memory usage:
# - Store processed article URLs
# - Track summaries from previous weeks
# - Remember user preferences
# - Cache site content patterns
```

## Configuration Architecture

### 1. News Sources Configuration (`config/news_sources.yaml`)

```yaml
# List of specific page URLs to check for news articles every week
# Agent will scrape these pages to discover article links
# All sources are checked weekly; topic priorities determine article selection
# Supports both HTML pages and RSS/Atom feeds
news_sources:
    tech:
        pages:
            - url: "https://feeds.arstechnica.com/arstechnica/index"
              name: "Ars Technica - RSS Feed"
              type: "rss" # Optional: specify if rss feed or html
            - url: "https://news.ycombinator.com/rss"
              name: "HackerNews - RSS Feed"
              type: "rss"
            - url: "https://www.theverge.com/rss/index.xml"
              name: "The Verge - RSS Feed"
              type: "rss"

    hackathons:
        pages:
            - url: "https://devpost.com/hackathons?challenge_type[]=online&order_by=prize-amount"
              name: "Devpost Hackathons"
              type: "html"
            - url: "https://www.hackster.io/contests"
              name: "Hackster.io Contests"
              type: "html"
            - url: "https://www.kaggle.com/competitions"
              name: "Kaggle Competitions"
              type: "html"
    ai:
        pages:
            - url: "https://blog.google/products/gemini/rss/"
              name: "Google Gemini - RSS Feed"
              type: "rss"
            - url: "https://openai.com/news/"
              name: "OpenAI News"
              type: "html"
            - url: "https://www.anthropic.com/news"
              name: "Anthropic News"
              type: "html"
    maker:
        pages:
            - url: "https://blog.arduino.cc/feed/"
              name: "Arduino - RSS Feed"
              type: "rss"
            - url: "https://www.raspberrypi.com/news/feed/"
              name: "Raspberry Pi - RSS Feed"
              type: "rss"
            - url: "https://makezine.com/feed"
              name: "Make Magazine - RSS Feed"
              type: "rss"
    webdev:
        pages:
            - url: "https://web.dev/static/blog/feed.xml"
              name: "Google Web.dev - RSS Feed"
              type: "rss"
```

### 2. Topic Priorities (`config/topic_priorities.yaml`)

```yaml
# Topic priorities help the LLM select the top 20 articles from all discovered content
# Higher priority = more likely to be included in the weekly summary
# User bookmarks always get highest priority (11) automatically
topics:
    - name: "Hackathons"
      keywords: ["hackathon"]
      priority: 9

    - name: "Web Development"
      keywords: ["html", "React", "CSS", "frontend", "WordPress"]
      priority: 5

    - name: "Programming"
      keywords: ["Python", "JavaScript", "TypeScript"]
      priority: 7

    - name: "Maker"
      keywords:
          ["Maker", "3d printer", "circuit", "arduino", "raspberry pi", "led"]

    - name: "AI"
      keywords: ["Gemini", "OpenAI", "Anthropic", "Nano Banana"]
      priority: 8
```

### 3. Weekly Bookmarks (`config/weekly_bookmarks.yaml`)

```yaml
# Ephemeral list of user-submitted bookmarks for the current week
# This file is updated weekly with articles you want included
# Bookmarks always get highest priority (11) in article selection
bookmarks:
    - url: "https://example.com/interesting-article-1"
      note: "Optional note about why this is interesting"
      submitted_date: "2025-11-25"

    - url: "https://example.com/another-article"
      note: "Check out the section on performance"
      submitted_date: "2025-11-26"
# This file can be:
# - Manually edited
# - Generated by a script
# - Eventually managed via admin UI or Chrome extension
```

### 4. WordPress Configuration (`config/wordpress.yaml`)

```yaml
wordpress:
    site_url: "https://mkfoster.com"
    api_endpoint: "/wp-json/wp/v2"

    # Credentials stored in environment variables
    # WORDPRESS_USERNAME
    # WORDPRESS_APP_PASSWORD

    post_defaults:
        status: "private"
        categories: ["WeeklySummary"]
        format: "standard"

    featured_image:
        aspect_ratio: "3:2"
        min_width: 1200
        quality: 90
```

### 5. Writing Style Configuration (`config/writing_style.yaml`)

```yaml
style_examples:
    source_sites:
        - "https://mkfoster.com"
        - "https://fireflywp.com"

    characteristics:
        - "Clear and concise technical writing"
        - "Conversational but professional tone"
        - "Use of concrete examples"
        - "Actionable insights"

    newsletter_format:
        title_pattern: "Mark's Weekly Update: {date}"
        date_format: "%B %dth, %Y"
        excerpt_length: "150-200 words"
        item_summary_length: "~200 tokens (roughly 150 words)"

    summary_structure:
        - section: "Introduction"
          content: "Brief overview of the week's themes"
        - section: "Articles"
          content: "20 article summaries with links"
        - section: "Conclusion"
          content: "Key takeaways or themes"
```

### 6. Environment Variables (`.env`)

```env
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE

# WordPress
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Datadog
DD_API_KEY=your-datadog-api-key
DD_SITE=datadoghq.com

# Optional: Override default weekly_bookmarks.yaml location
# BOOKMARK_CONFIG_PATH=gs://your-bucket/bookmarks/weekly_bookmarks.yaml

# Image Generation
IMAGEN_PROJECT_ID=your-project-id
IMAGEN_LOCATION=us-central1
```

## Project Structure

```
mynewsrobot/
├── README.md
├── Requirements.md
├── Architecture.md
├── PROJECT_PLAN.md
├── pyproject.toml                    # Python project config
├── requirements.txt                  # Dependencies
├── .env.example                      # Environment template
├── Dockerfile                        # Cloud Run container
├── .dockerignore
│
├── config/                           # Configuration files
│   ├── news_sources.yaml
│   ├── topic_priorities.yaml
│   ├── weekly_bookmarks.yaml
│   ├── wordpress.yaml
│   └── writing_style.yaml
│
├── src/
│   ├── __init__.py
│   │
│   ├── agents/                       # Agent definitions
│   │   ├── __init__.py
│   │   ├── news_research_agent.py
│   │   ├── content_extraction_agent.py
│   │   ├── content_analysis_agent.py
│   │   ├── content_writing_agent.py
│   │   ├── image_generation_agent.py
│   │   └── publishing_agent.py
│   │
│   ├── tools/                        # Custom tools
│   │   ├── __init__.py
│   │   ├── web_scraper_tool.py
│   │   ├── wordpress_tool.py
│   │   ├── imagen_tool.py
│   │   └── bookmark_loader_tool.py
│   │
│   ├── workflow/                     # Orchestration
│   │   ├── __init__.py
│   │   └── weekly_summary_workflow.py
│   │
│   ├── utils/                        # Utilities
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   ├── date_formatter.py
│   │   └── memory_manager.py
│   │
│   └── main.py                       # Entry point
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_tools/
│   └── test_workflow/
│
├── docs/                             # Documentation
│   ├── setup.md
│   ├── deployment.md
│   └── usage.md
│
└── cloudbuild.yaml                   # Cloud Build config
```

## Key Dependencies

```txt
# requirements.txt
google-adk[all]>=0.1.0
google-cloud-aiplatform>=1.60.0
google-genai>=0.1.0
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.0.0
pyyaml>=6.0.1
requests>=2.31.0
beautifulsoup4>=4.12.0
newspaper3k>=0.2.8
feedparser>=6.0.10                    # RSS/Atom feed parsing
python-dotenv>=1.0.0
ddtrace>=2.0.0                        # Datadog tracing
```

## Datadog Observability Strategy

### Monitoring Components

1. **LLM Telemetry**

    - Token usage per agent
    - Response times
    - Error rates
    - Model performance metrics

2. **Application Metrics**

    - Articles processed per run
    - Success/failure rates by source
    - Memory usage
    - API call counts (WordPress, Imagen)

3. **Detection Rules**

    - Alert if agent run takes > 30 minutes
    - Alert if fewer than 10 articles found
    - Alert if WordPress publishing fails
    - Alert if Gemini error rate > 10%

4. **Dashboard Components**
    - Agent execution timeline
    - Article source breakdown
    - Topic distribution
    - Cost tracking (LLM tokens, API calls)
    - Weekly summary metrics

### Implementation

```python
# src/utils/datadog_telemetry.py
from ddtrace import tracer, patch_all
import ddtrace.auto

# Patch all supported libraries
patch_all()

# Custom metrics
from datadog import statsd

def track_agent_execution(agent_name, duration, success):
    statsd.increment(f'mynewsrobot.agent.execution.{agent_name}')
    statsd.histogram(f'mynewsrobot.agent.duration.{agent_name}', duration)
    if not success:
        statsd.increment(f'mynewsrobot.agent.error.{agent_name}')

def track_article_processing(count, source):
    statsd.gauge('mynewsrobot.articles.processed', count)
    statsd.increment(f'mynewsrobot.source.{source}')
```

## Deployment Strategy

### Local Development

```bash
# Setup
python3.13 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Run locally
python src/main.py
```

### Cloud Run Deployment

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/mynewsrobot
gcloud run deploy mynewsrobot \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/mynewsrobot \
  --platform managed \
  --region $GOOGLE_CLOUD_LOCATION \
  --no-allow-unauthenticated \
  --set-env-vars-file .env.yaml \
  --memory 2Gi \
  --timeout 3600 \
  --max-instances 1

# Or use ADK CLI
adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=mynewsrobot \
  --trace_to_cloud \
  .
```

### Cloud Scheduler Setup

```bash
# Create Cloud Scheduler job to run every Sunday at 6 AM
gcloud scheduler jobs create http mynewsrobot-weekly \
  --schedule="0 6 * * 0" \
  --time-zone="America/Chicago" \
  --uri="https://mynewsrobot-xxxxx-uc.a.run.app/run" \
  --http-method=POST \
  --oidc-service-account-email=mynewsrobot@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

-   ✅ Set up project structure
-   ✅ Install dependencies
-   ✅ Create configuration system
-   ✅ Set up Gemini 2.5 Flash connection
-   ✅ Implement basic memory service

### Phase 2: Tools Development (Week 2)

-   ✅ Build WebScraperTool (supports RSS feeds and HTML pages)
-   ✅ Build BookmarkLoaderTool
-   ✅ Build WordPressTool (basic version)
-   ✅ Unit tests for all tools

### Phase 3: Agent Development (Week 3)

-   ✅ NewsResearchAgent (discovers articles from configured pages)
-   ✅ ContentExtractionAgent (optimized for RSS content tags)
-   ✅ ContentAnalysisAgent
-   ✅ ContentWritingAgent with style learning (~200 tokens per item)
-   ✅ Integration tests

### Phase 4: Core Workflow & Publishing (Week 4)

-   ✅ SequentialAgent orchestration
-   ✅ PublishingAgent
-   ✅ End-to-end workflow testing (without images)
-   ✅ Verify weekly summaries are generated and posted

### Phase 5: Deployment & Observability (Week 5)

-   ✅ Datadog integration
-   ✅ Cloud Run containerization
-   ✅ Cloud Scheduler setup
-   ✅ Production testing
-   ✅ Documentation

### Phase 6: Image Generation Integration (Week 6)

-   ✅ Build ImagenTool
-   ✅ Implement ImageGenerationAgent
-   ✅ Integrate into workflow (optional step)
-   ✅ Generate featured images (3:2 ratio)
-   ✅ Generate article-specific images
-   ✅ Update WordPress posts with images
-   ✅ Test image quality and relevance

### Phase 7: Future Enhancements

-   🔄 Admin web interface for configuration
-   🔄 Chrome extension for bookmark submission
-   🔄 Audio podcast generation (stretch goal)
-   🔄 Google Veo animated visuals (stretch goal)

## Success Criteria

### Functional Requirements

-   ✅ Successfully discovers 30+ relevant articles weekly
-   ✅ Prioritizes user bookmarks correctly
-   ✅ Selects top 20 most relevant articles
-   ✅ Writes summaries in Mark's style (~200 tokens each)
-   ✅ Efficiently uses RSS content tags when available
-   ✅ Posts to WordPress successfully
-   ✅ (Phase 6) Generates appropriate images
-   ✅ Runs automatically on schedule
-   ✅ No duplicate articles across weeks

### Quality Requirements

-   ✅ Summaries are accurate and well-written
-   ✅ Citations and links are correct
-   ✅ Newsletter format is consistent
-   ✅ (Phase 6) Images are relevant and visually appealing
-   ✅ Execution time < 30 minutes
-   ✅ Success rate > 95%

### Observability Requirements (Datadog)

-   ✅ Real-time dashboard shows agent health
-   ✅ Alerts trigger on failures
-   ✅ LLM telemetry tracked and visualized
-   ✅ Cost metrics available
-   ✅ Actionable incidents created on errors

## Cost Estimates

### Google Cloud

-   **Gemini 2.5 Flash**: ~$0.50-2.00 per weekly run (depends on article count)
-   **Cloud Run**: ~$0.10 per run (minimal, 30-min execution)
-   **Cloud Scheduler**: $0.10/month
-   **Imagen (Phase 6)**: ~$2.00-5.00 per week (20+ images)
-   **Total GCP (Phases 1-5)**: ~$10-15/month
-   **Total GCP (with Phase 6)**: ~$15-30/month

### Datadog

-   **Pro plan**: $15/host/month (includes APM, infrastructure monitoring)
-   **LLM Observability**: May require additional features

### Total Estimated Cost

-   **Monthly (Phases 1-5)**: $25-30 (primarily Datadog)
-   **Monthly (with Phase 6)**: $30-50 (Datadog and Imagen)

## Risks & Mitigations

| Risk                           | Impact | Mitigation                                                    |
| ------------------------------ | ------ | ------------------------------------------------------------- |
| Website blocking/rate limiting | High   | Implement respectful scraping with delays, user-agent headers |
| WordPress API failures         | High   | Retry logic, save draft locally on failure                    |
| Gemini quota/cost overruns     | Medium | Set token limits, monitor costs with Datadog                  |
| Article quality issues         | Medium | Implement evaluation metrics, manual review initially         |
| Memory service failures        | Low    | Graceful degradation, manual deduplication fallback           |

## Next Steps

1. **Review and approve this plan**
2. **Set up Google Cloud project and enable APIs**
3. **Configure Datadog account**
4. **Begin Phase 1 implementation**
5. **Schedule weekly sync meetings to track progress**

---

**Questions or Clarifications Needed:**

1. Preferred visual style for generated images?
2. Specific WordPress theme requirements?
3. How will you update weekly_bookmarks.yaml each week (manual edit, script, cloud storage)?
4. Preferred time/day for weekly execution?
5. Ready to provide your actual news source URLs (RSS feeds preferred where available)?
