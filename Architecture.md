Here is my thinking for architecture.  Let me know if there are better alternatives or opportunities here:
!Important! Google ADK to build a multi-agent sequential workflow.  At least a couple agents to do the research and write up the weekly summary.  Identify what makes sense as a tool and what makes sense as an agent.
Here is the latest Google ADK documentation: https://google.github.io/adk-docs/
The project should be built in Python and specifically language features supported in Python 3.13 (latest stable Cloud Run base image per https://docs.cloud.google.com/run/docs/runtimes/python)
Use the Google search tool to harvest news stories, articles, etc.  Does it just search or can it also read the site/page content given a URL?
Leverage context/memory to avoid duplication from previous weeks as noted.
Utilize the latest Gemini Flash model (2.5).  If that doesn’t perform well we can bump it up to Pro.
Deploy using Google Cloud Run Jobs and run it weekly using Google Cloud Scheduler.
Use the WordPress API to post weekly summaries to my blog site automatically.  Posts will be private initially and have a “WeeklySummary” category so I can filter them over to a separate blog page from my normal blog.
Datadog Challenge: I will be cross-posting this project to a Google partner hackathon with Data Dog.  Here is the requirement for that project:   Datadog Challenge: Using Datadog, implement an innovative end-to-end observability monitoring strategy for an LLM application (new or reused) of your choice, powered by Vertex AI or Gemini. Stream LLM and runtime telemetry to Datadog, define detection rules, and present a clear dashboard that surfaces application health and the observability/security signals you consider essential. When any detection rule is triggered, leverage Datadog to define an actional item (e.g., case, incident, alert, etc.) with context for an AI engineer to act on.  You have full access to Datadog, be creative in how you leverage the platform and the telemetry you emit.
Let me know your thoughts on the requirements and architecture please.  Thanks.
