# MyNewsRobot - Architecture Documentation

## Overview

MyNewsRobot is an intelligent RSS aggregator and newsletter generator that uses Google's Agent Development Kit (ADK) to orchestrate a multi-agent workflow. The system discovers articles from RSS feeds, analyzes them based on user-defined topic priorities, generates personalized summaries, and publishes weekly newsletters to WordPress.

## Project Philosophy

This is a **smart RSS reader**, not a web scraper:

-   All content sources are RSS feeds only
-   No HTML parsing or full article extraction
-   Uses RSS excerpts as the foundation for summaries
-   Focuses on curation and personalization rather than content extraction

## Technology Stack

-   **Language**: Python 3.13
-   **AI Framework**: Google Agent Development Kit (ADK)
-   **LLM Model**: Gemini 2.5 Flash (with Pro as fallback)
-   **Web Framework**: FastAPI
-   **Deployment**: Google Cloud Run
-   **Scheduler**: Google Cloud Scheduler (weekly execution)
-   **Publishing**: WordPress REST API with Application Passwords
-   **Observability**: Datadog (monitoring, telemetry, alerts) (work-in-progress)

## Architecture Components

### 1. Core Workflow (Sequential Multi-Agent)

```
┌─────────────────────────────────────────────────────────────┐
│                     MyNewsRobot Workflow                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Discovery (news_scraper.py)                       │
│  📰 Fetch articles from RSS feeds                           │
│  → Output: discovered_articles.json (~100+ articles)        │
│                                                              │
│  Step 2: Analysis (ContentAnalysisAgent)                    │
│  🔍 Load topic priorities                                   │
│  🔍 Match articles to topics by keywords                    │
│  🔍 Rank by priority (7-11 scale)                          │
│  🔍 Select top 20 (max 10 per topic for diversity)         │
│  → Output: analyzed_articles.json (20 articles)             │
│                                                              │
│  Step 3: Writing (ContentWritingAgent)                      │
│  ✍️ Generate personalized summaries (~150 words each)      │
│  ✍️ Format as HTML for WordPress                           │
│  → Output: newsletter_draft.html                            │
│                                                              │
│  Step 4: Publishing (PublishingAgent)                       │
│  🚀 Create private WordPress post                          │
│  🚀 Add "WeeklySummary" category                           │
│  → Output: WordPress post URL                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Agents

#### ContentAnalysisAgent

-   **Purpose**: Select top 20 articles based on topic priorities
-   **Model**: Gemini 2.5 Flash
-   **Tools**:
    -   `get_topic_priorities()` - Loads topic configuration with priority scores and keywords
-   **Input**: List of discovered articles (RSS metadata)
-   **Output**: JSON array of 20 articles with priority and matched_topic fields
-   **Logic**:
    1. Call `get_topic_priorities()` to get topics with scores (7-11) and keywords
    2. Match each article's title/excerpt against topic keywords
    3. Assign priority score based on matched topic
    4. Bookmarks automatically get priority 11
    5. Select top 20, max 10 per topic for diversity
    6. Prefer recent articles when priorities are equal

#### ContentWritingAgent

-   **Purpose**: Write personalized newsletter summaries
-   **Model**: Gemini 2.5 Flash
-   **Tools**: None (pure LLM generation)
-   **Input**: 20 analyzed articles with priorities
-   **Output**: HTML newsletter content
-   **Logic**:
    1. Load writing style guidelines from config
    2. Write ~150-word summary for each article
    3. Expand on RSS excerpt with personal perspective
    4. Format as clean HTML (no title, starts with intro paragraph)
    5. Use ordered list for articles with H3 headings

#### PublishingAgent

-   **Purpose**: Publish newsletter to WordPress
-   **Model**: Gemini 2.5 Flash
-   **Tools**:
    -   `publish_to_wordpress()` - WordPress REST API integration
-   **Input**: Newsletter HTML, title, excerpt
-   **Output**: WordPress post ID, URLs (post URL, edit URL)
-   **Logic**:
    1. Receive formatted newsletter and metadata
    2. Call `publish_to_wordpress()` with parameters
    3. Create private post with "WeeklySummary" category
    4. Return confirmation with URLs

### 3. Tools

#### News Discovery

-   **`news_scraper.py`**: RSS feed aggregator
    -   Enforces RSS-only sources (validates feed type)
    -   Fetches from multiple categories (tech, AI, WordPress, etc.)
    -   Outputs: URL, title, excerpt, source, category, published_date, is_bookmark
    -   No HTML parsing or content extraction
    -   Uses feedparser library for RSS parsing

#### Topic Prioritization

-   **`get_topic_priorities()`**: Loads topic configuration
    -   Returns topics with priority scores (7-11 scale)
    -   Includes keywords for topic matching
    -   Configuration file: `config/topic_priorities.yaml`
    -   Example topics: AI/ML, WordPress, Web Development, Cloud Computing

#### WordPress Publishing

-   **`publish_to_wordpress()`**: WordPress REST API client
    -   Uses Application Password authentication (Basic Auth)
    -   Creates posts with title, content, status, categories, excerpt
    -   Automatically creates "WeeklySummary" category if needed
    -   Returns post ID, post URL, edit URL, status
    -   Handles authentication with username and app-specific password

#### User Bookmarks

-   **`load_user_bookmarks()`**: Loads weekly bookmarks
    -   Reads from `config/weekly_bookmarks.yaml`
    -   Bookmarks get automatic priority 11 (always included)
    -   Allows manual curation alongside automated discovery

### 4. Configuration Files

```
config/
├── news_sources.yaml          # RSS feed URLs by category
├── topic_priorities.yaml      # Topics with priority scores & keywords
├── weekly_bookmarks.yaml      # User-curated articles (priority 11)
├── writing_style.yaml         # Writing guidelines and examples
└── wordpress_config.yaml      # WordPress site URL and API settings
```

### 5. Data Flow

```
RSS Feeds → news_scraper.py → discovered_articles.json (100+ articles)
                                         ↓
                              ContentAnalysisAgent + get_topic_priorities()
                                         ↓
                              analyzed_articles.json (20 articles with priorities)
                                         ↓
                              ContentWritingAgent
                                         ↓
                              newsletter_draft.html (formatted HTML)
                                         ↓
                              PublishingAgent + publish_to_wordpress()
                                         ↓
                              WordPress Private Post (mkfoster.com)
```

### 6. API Endpoints

**FastAPI Server** (port 8080)

-   `POST /run` - Execute full workflow

    -   Body: `{"newsletter_date": "December 1, 2025"}`
    -   Returns: execution status, article count, post URL, execution time

-   `GET /config/status` - Configuration validation
    -   Returns: news sources count, topics count, bookmarks count, API status

### 7. Environment Variables

```env
# Google AI
GOOGLE_API_KEY=...                    # Google AI Studio API key
GOOGLE_CLOUD_PROJECT=mynewsrobot-...  # GCP project ID
GOOGLE_CLOUD_LOCATION=us-central1     # Region for Vertex AI

# WordPress
WORDPRESS_USERNAME=...                # WordPress username
WORDPRESS_APP_PASSWORD=...            # Application-specific password (spaces removed automatically)

# Datadog
DD_API_KEY=...                        # Datadog API key
DD_SITE=datadoghq.com                # Datadog site
DD_ENV=development                    # Environment name
DD_SERVICE=mynewsrobot               # Service name
DD_VERSION=0.1.0                     # Version tracking
```

## Key Design Decisions

### RSS-Only Architecture

-   **Why**: Reliable, consistent, lightweight, respects site preferences
-   **Trade-off**: Limited to RSS excerpt length, no full article content
-   **Benefit**: Fast, scalable, no HTML parsing complexity
-   **Decision Point**: Week 2 - Eliminated ContentExtractionAgent after realizing RSS excerpts were sufficient

### 3-Agent Sequential Workflow

-   **Original Plan**: 6 agents (Research, Extraction, Analysis, Writing, Image Generation, Publishing)
-   **Final Implementation**: 3 agents (Analysis, Writing, Publishing)
-   **Removed**:
    -   NewsResearchAgent (replaced with simple news_scraper.py script)
    -   ContentExtractionAgent (unnecessary with RSS-only approach)
    -   ImageGenerationAgent (deferred to future enhancement)
-   **Benefit**: Simpler, faster, fewer API calls, easier to debug

### Topic Diversity (10 Articles Per Topic Max)

-   **Why**: Prevent single topic from dominating newsletter
-   **How**: ContentAnalysisAgent enforces cap during selection
-   **Benefit**: Balanced, diverse content across interests
-   **Example**: Prevents all 20 articles from being about AI/ML

### Private WordPress Posts

-   **Why**: Manual review before public visibility
-   **How**: Posts created with status="private" and "WeeklySummary" category
-   **Benefit**: Quality control, safe automation, can edit before publishing

### Application Password Authentication

-   **Why**: WordPress standard for REST API access (available since WordPress 5.6)
-   **How**: Basic Auth with username and app-specific password
-   **Benefit**: Secure, revocable, no main password exposure
-   **Implementation**: Spaces automatically removed from password before use

### Google ADK Integration

-   **Why**: Official Google framework for multi-agent orchestration
-   **How**: Agent class with tools, sequential workflow, session management
-   **Benefit**: Built-in tracing, error handling, consistent patterns
-   **Challenge**: Learning curve for agent/tool architecture

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the server
python src/main.py

# Trigger workflow
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"newsletter_date": "December 1, 2025"}'
```

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/mynewsrobot
gcloud run deploy mynewsrobot \
  --image gcr.io/PROJECT_ID/mynewsrobot \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=...,WORDPRESS_USERNAME=...
```

### Google Cloud Scheduler (Weekly)

```bash
gcloud scheduler jobs create http weekly-newsletter \
  --schedule="0 9 * * 1" \
  --uri=https://mynewsrobot-xxx.run.app/run \
  --http-method=POST \
  --message-body='{"newsletter_date":"current"}' \
  --time-zone="America/New_York"
```

## Observability (Datadog)

### Telemetry Streams

-   **LLM Metrics**: Token usage, latency, errors, cost per request
-   **Agent Traces**: Execution time, success/failure, tool calls made
-   **API Performance**: Request rate, response time, status codes
-   **Publishing Metrics**: WordPress API success rate, post creation time

### Detection Rules

1. **High LLM Error Rate**: > 5% errors in 5 minutes → Alert
2. **Workflow Failure**: Any step fails → Create incident
3. **WordPress Auth Failure**: 401/403 errors → Alert
4. **Slow Execution**: Total workflow > 30 seconds → Warning
5. **Low Article Count**: < 10 articles discovered → Alert

### Dashboard Metrics

-   Articles discovered per run
-   Agent execution time breakdown (pie chart)
-   Token usage and cost tracking (time series)
-   Publication success rate (gauge)
-   Error rates by component (bar chart)
-   Topic distribution analysis (pie chart)

### Alerts & Incidents

-   **Workflow Failure** → Incident with full trace context, LLM logs, error stack
-   **High Error Rate** → Alert to on-call engineer with recent error samples
-   **Cost Threshold** → Budget warning when token usage exceeds threshold
-   **Authentication Failure** → Security alert with IP and timestamp

## Testing Strategy

### Unit Tests

-   Agent configuration and initialization
-   Tool function behavior (RSS parsing, WordPress API)
-   Configuration file loading and validation
-   Data transformation and JSON parsing

### Integration Tests

-   Full workflow execution (discover → analyze → write → publish)
-   Agent tool calling and response parsing
-   WordPress API authentication and post creation
-   Error handling and fallback behavior

### Test Fixtures

-   Sample RSS feeds (mocked responses)
-   Sample discovered articles (JSON)
-   Sample WordPress API responses
-   Mock LLM responses for deterministic testing

## Performance Characteristics

### Execution Time

-   **Discovery**: ~5-10 seconds (100+ RSS feeds)
-   **Analysis**: ~3-5 seconds (topic matching and ranking)
-   **Writing**: ~10-15 seconds (newsletter generation)
-   **Publishing**: ~2-3 seconds (WordPress API call)
-   **Total**: ~20-30 seconds end-to-end

### Cost Analysis

-   **LLM Tokens**: ~50,000 tokens per run (input + output)
-   **Gemini 2.5 Flash**: ~$0.10 per run
-   **Cloud Run**: Minimal (< $1/month for weekly runs)
-   **Total Monthly Cost**: < $5/month

### Scalability

-   Can handle 500+ RSS feeds
-   Supports 1000+ articles in analysis phase
-   WordPress API has no rate limits for authenticated users
-   Cloud Run auto-scales (though single instance is sufficient)

## Security Considerations

### Credentials Management

-   All secrets in environment variables (never committed)
-   WordPress Application Passwords (revocable, app-specific)
-   Google API keys with IP restrictions
-   Datadog API keys with minimal permissions

### Data Privacy

-   No user data collected or stored
-   RSS feeds are public data
-   WordPress posts are private by default
-   No PII in logs or traces

### Network Security

-   HTTPS for all API calls
-   WordPress REST API over TLS
-   Cloud Run with IAM authentication
-   No public database or storage

## Troubleshooting Guide

### Common Issues

**1. Agent not calling tools**

-   Check agent instruction clarity
-   Verify tool is in tools array
-   Simplify prompt to be more explicit
-   Check for default parameter issues (Google AI doesn't support)

**2. WordPress 401 errors**

-   Verify Application Password is correct
-   Check spaces are removed from password
-   Confirm user has Author/Editor role
-   Test with browser fetch() in dev tools

**3. JSON parsing failures**

-   Check regex pattern for JSON extraction
-   Add more explicit JSON-only instructions
-   Verify LLM is returning valid JSON
-   Add fallback behavior for parse errors

**4. All articles from one source**

-   Verify get_topic_priorities() is being called
-   Check 10-per-topic limit enforcement
-   Review topic keyword matching logic
-   Inspect analyzed_articles.json for priority/matched_topic fields

**5. Duplicate title in WordPress**

-   Ensure writing agent doesn't include H1 title
-   WordPress displays title separately
-   Update agent instruction to start with intro paragraph

## Future Enhancements

### Phase 1 (Next 3 months)

1. **Image Generation**: Add Imagen API integration for article visuals
2. **Email Distribution**: Send newsletter via SendGrid/Mailgun
3. **Better Topic Matching**: Use semantic similarity instead of keywords
4. **Memory Service**: Track previously seen articles across weeks

### Phase 2 (3-6 months)

5. **Web Admin Interface**: Manage sources and topics via React UI
6. **Chrome Extension**: Submit bookmarks with one click
7. **A/B Testing**: Test different writing styles, measure engagement
8. **Multi-language Support**: Generate newsletters in multiple languages

### Phase 3 (6-12 months - Stretch Goals)

9. **Audio Podcast**: Generate spoken version with Google TTS
10. **Video Summaries**: Use Google Veo for animated content
11. **User Feedback Loop**: Learn from engagement metrics
12. **Smart Scheduling**: Adjust delivery time based on open rates

## Project Evolution

### Initial Vision (Capstone Plan)

-   6 agents including research, extraction, image generation
-   Google Search tool for discovery
-   Full article extraction from web pages
-   Complex memory deduplication system

### Final Implementation

-   3 agents focusing on core value (analyze, write, publish)
-   RSS-only for reliable, lightweight discovery
-   Simple script for news scraping
-   Configuration-based approach (no complex state)

### Lessons Learned

1. **Simpler is better**: RSS excerpts were sufficient, no need for full extraction
2. **Tools vs Agents**: Not everything needs to be an agent
3. **Explicit instructions**: LLMs need very clear, direct prompts for tool calling
4. **Google ADK quirks**: Default parameters not supported, relative imports tricky
5. **WordPress API**: Application Passwords work great, well-documented

## References

-   **Google ADK Documentation**: https://google.github.io/adk-docs/
-   **WordPress REST API**: https://developer.wordpress.org/rest-api/
-   **Application Passwords Guide**: https://make.wordpress.org/core/2020/11/05/application-passwords-integration-guide/
-   **Datadog APM**: https://docs.datadoghq.com/tracing/
-   **Google Cloud Run**: https://cloud.google.com/run/docs
-   **Gemini API**: https://ai.google.dev/gemini-api/docs
-   **FastAPI**: https://fastapi.tiangolo.com/

---

**Project Status**: ✅ Core Implementation Complete

**Last Updated**: December 1, 2025

**Primary Contact**: Mark Foster
