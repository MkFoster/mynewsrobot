# MyNewsRobot - Capstone Project

## Executive Summary

MyNewsRobot is an intelligent AI agent system that autonomously creates personalized weekly news summaries and publishes them to WordPress. Built with Google's Agent Development Kit (ADK), it combines multiple specialized agents in a sequential workflow to research, analyze, write, illustrate, and publish curated content.

## Project Goals

1. **Automated News Curation**: Discover and aggregate relevant articles from specified sources and topics
2. **Intelligent Prioritization**: Rank content based on user-defined topic priorities and personal bookmarks
3. **Personalized Writing**: Generate summaries in the user's unique writing style
4. **Visual Enhancement**: Create AI-generated images to accompany articles
5. **Automated Publishing**: Post complete newsletters to WordPress on a weekly schedule
6. **Production-Ready Observability**: Implement comprehensive monitoring with Datadog

## Technical Innovation

### Multi-Agent Architecture

Uses Google ADK's SequentialAgent to orchestrate six specialized agents:

-   NewsResearchAgent - Discovers relevant content
-   ContentExtractionAgent - Fetches full article text
-   ContentAnalysisAgent - Ranks and selects top items
-   ContentWritingAgent - Generates summaries in user's style
-   ImageGenerationAgent - Creates visual content
-   PublishingAgent - Posts to WordPress

### Advanced Features

-   **Memory-based Deduplication**: Prevents duplicate articles across weeks
-   **Style Learning**: Analyzes writing samples to match user's voice
-   **Priority-based Selection**: Combines topic rankings with user bookmarks
-   **Scheduled Automation**: Weekly execution via Cloud Run Jobs + Cloud Scheduler

### Google Cloud Integration

-   Vertex AI for Gemini 2.5 Flash models
-   Cloud Run for serverless execution
-   Cloud Scheduler for automated triggers
-   Imagen API for image generation
-   Cloud Build for CI/CD

## Datadog Challenge Integration

### End-to-End Observability Strategy

**LLM Telemetry Streaming**:

-   Token usage tracking per agent
-   Model performance metrics (latency, success rate)
-   Cost tracking for Gemini API calls
-   Error rate monitoring

**Detection Rules**:

1. Alert if weekly run exceeds 30 minutes
2. Alert if fewer than 10 articles discovered
3. Alert if WordPress publishing fails
4. Alert if Gemini error rate > 10%
5. Alert if memory deduplication fails

**Dashboard Components**:

-   Real-time agent execution timeline
-   Article source breakdown (pie chart)
-   Topic distribution analysis
-   Cost tracking (tokens, API calls, compute)
-   Success/failure metrics by agent
-   Weekly trends and comparisons

**Actionable Incidents**:
When detection rules trigger, Datadog creates incidents with:

-   Full trace context showing which agent failed
-   LLM request/response logs
-   Error stack traces
-   Suggested remediation based on error type
-   Links to relevant documentation

### Security Signals

-   Monitor for unusual API usage patterns
-   Track authentication failures
-   Alert on unexpected data access
-   Monitor for content quality anomalies

## Business Value

1. **Time Savings**: Automates 3-4 hours of manual curation weekly
2. **Consistency**: Ensures weekly content publication without fail
3. **Personalization**: Delivers content precisely matched to interests
4. **Quality**: AI-powered summaries with proper citations
5. **Scalability**: Easy to add new sources and topics
6. **Observability**: Complete visibility into system health

## Success Metrics

-   **Execution Success Rate**: > 95%
-   **Content Quality**: Summaries match writing style (evaluated by user)
-   **Relevance**: > 90% of articles deemed useful
-   **Performance**: Complete execution in < 30 minutes
-   **Cost Efficiency**: < $50/month operational cost
-   **Reliability**: Zero missed weekly publications

## Future Enhancements

1. **Web Admin Interface**: Manage sources and topics via UI
2. **Chrome Extension**: Submit bookmarks with one click
3. **Audio Podcast**: Generate spoken version of newsletter (stretch)
4. **Animated Visuals**: Use Google Veo for video content (stretch)
5. **Multi-destination Publishing**: Support additional platforms
6. **A/B Testing**: Experiment with different writing styles

## Timeline

-   **Week 1**: Core infrastructure and configuration
-   **Week 2**: Custom tools development
-   **Week 3**: Agent implementation
-   **Week 4**: Workflow orchestration and testing
-   **Week 5**: Deployment and Datadog integration
-   **Week 6+**: Enhancements and optimization

## Technologies Used

-   Python 3.13
-   Google Agent Development Kit (ADK)
-   Google Cloud Platform (Vertex AI, Cloud Run, Cloud Scheduler)
-   Gemini 2.5 Flash (LLM)
-   Imagen API (Image Generation)
-   WordPress REST API
-   Datadog (Observability)
-   Docker (Containerization)

---

**Project Status**: Planning Complete - Ready for Implementation

**Primary Contact**: Mark Foster
