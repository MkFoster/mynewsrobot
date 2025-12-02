# MyNewsRobot - Requirements

## Project Overview
MyNewsRobot is an intelligent AI agent system that creates personalized weekly news summaries and publishes them to WordPress. Built with Google's Agent Development Kit (ADK), it aggregates content from RSS feeds, analyzes and prioritizes articles based on user-defined topics, and generates summaries in a consistent style.

## Core Requirements

### Technology Stack
- ✅ **Built with Google ADK** - Multi-agent orchestration framework
- ✅ **Python 3.14** - Primary development language
- ✅ **Gemini 2.5 Flash** - LLM model for all agents
- ✅ **FastAPI** - REST API server for workflow execution
- ✅ **WordPress REST API** - Publishing endpoint with Application Password authentication

### Content Discovery
- ✅ **RSS Feed Sources** - All news sources are RSS feeds configured in `config/news_sources.yaml`
- ✅ **Category Organization** - Sources organized by category (Tech, AI, WordPress, Security, etc.)
- ✅ **RSS-Only Architecture** - Uses RSS excerpts only, no web scraping or HTML parsing
- ✅ **User Bookmarks** - Weekly bookmarks file (`config/weekly_bookmarks.yaml`) for manual article submission
- ✅ **Automatic Priority** - Bookmarks automatically get highest priority (11) and are always included

### Topic Prioritization
- ✅ **Topic Configuration** - Topics defined in `config/topic_priorities.yaml` with priority scores (7-11 scale)
- ✅ **Keyword Matching** - Articles matched to topics based on keywords
- ✅ **Priority-Based Selection** - Top 20 articles selected based on topic priorities
- ✅ **Topic Diversity** - Maximum 10 articles per topic to ensure variety
- ✅ **Bookmark Override** - Bookmarks always included regardless of topic limits

### Content Generation
- ✅ **Writing Style Guidelines** - Style configuration in `config/writing_style.yaml`
- ✅ **Style References** - Based on articles from mkfoster.com and fireflywp.com
- ✅ **Article Summaries** - ~150 words per article, expanding on RSS excerpt
- ✅ **Source Citations** - All summaries include links to original articles
- ✅ **AI Attribution** - Header "From MyNewsRobot:" identifies AI-generated content
- ✅ **Neutral Voice** - No personal pronouns in intro/conclusion to clarify content is bot-generated
- ✅ **HTML Formatting** - Clean semantic HTML for WordPress

### Newsletter Format
- ✅ **Title Format** - "Mark's Weekly Update: [Date]" (e.g., "Mark's Weekly Update: November 30th, 2025")
- ✅ **Excerpt** - 150-200 word summary for WordPress post preview
- ✅ **Structure** - H2 header ("From MyNewsRobot:"), intro paragraph, 20 numbered articles, conclusion
- ✅ **Content Organization** - Ordered list with H3 headings for each article title

### WordPress Publishing
- ✅ **Automated Publishing** - Publishes to WordPress via REST API
- ✅ **Private Posts** - Creates private posts for manual review before public visibility
- ✅ **Category Assignment** - Automatically assigns "WeeklySummary" category
- ✅ **Application Password Auth** - Uses WordPress Application Passwords (Basic Auth)
- ✅ **Post Metadata** - Includes title, excerpt, content, status, and categories

### Workflow Execution
- ✅ **Multi-Agent Architecture** - 3 sequential agents:
  - ContentAnalysisAgent - Selects top 20 articles based on priorities
  - ContentWritingAgent - Generates newsletter content in user's style
  - PublishingAgent - Publishes to WordPress
- ✅ **FastAPI Endpoint** - `/run` endpoint to trigger workflow
- ✅ **Data Persistence** - Saves intermediate results (discovered_articles.json, analyzed_articles.json, newsletter_draft.html)
- ✅ **Error Handling** - Comprehensive logging and error recovery
- ⏳ **Weekly Scheduling** - Cloud Scheduler integration (deployment pending)

### Observability
- ⏳ **Datadog Integration** - Telemetry, metrics, and alerts (planned)
- ⏳ **LLM Metrics** - Token usage, latency, cost tracking (planned)
- ⏳ **Detection Rules** - Alerts for failures, slow execution, low article count (planned)
- ⏳ **Dashboards** - Workflow metrics, topic distribution, success rates (planned)

## Future Enhancements

### Phase 1: Visual Content (Deferred)
- 🎯 **AI-Generated Images** - Use Google Imagen for article visuals
- 🎯 **Featured Image** - Generate themed image (3:2 aspect ratio) for each newsletter
- 🎯 **Visual Variety** - Select key articles for image generation (not every article)

### Phase 2: User Interface
- 🎯 **Web Admin Interface** - Manage sources, topics, and bookmarks via UI
- 🎯 **Chrome Extension** - Submit bookmarks with one click during browsing
- 🎯 **Configuration Editor** - Visual editor for YAML configuration files

### Phase 3: Enhanced Distribution
- 🎯 **Email Delivery** - Send newsletter via email (SendGrid/Mailgun)
- 🎯 **Multi-Platform Publishing** - Support additional publishing platforms
- 🎯 **Public Post Option** - Automatic public publishing after manual review

### Stretch Goals
- 🚀 **Audio Podcast** - Generate spoken version of newsletter using Google TTS
- 🚀 **Video Animations** - Use Google Veo to create animated visuals for weekly themes
- 🚀 **Semantic Topic Matching** - Use embeddings instead of keyword matching
- 🚀 **Engagement Analytics** - Track reader engagement and adjust content selection
- 🚀 **Multi-Language Support** - Generate newsletters in multiple languages
- 🚀 **Smart Scheduling** - Optimize delivery time based on engagement patterns

## Implementation Status

### ✅ Completed (v0.1.0)
- Multi-agent workflow with Google ADK
- RSS-only content discovery
- Topic-based prioritization with bookmarks
- Newsletter generation with style guidelines
- WordPress publishing with Application Passwords
- AI attribution and neutral voice
- Comprehensive testing (62 tests passing)
- Local development environment

### ⏳ In Progress
- Google Cloud Run deployment
- Cloud Scheduler integration
- Datadog observability

### 🎯 Planned
- Image generation (Imagen API)
- Web admin interface
- Chrome extension
- Email distribution

### 🚀 Future Exploration
- Audio podcast generation
- Video animations (Veo)
- Advanced analytics
