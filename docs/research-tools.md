# Required Research Capabilities

The AI Intelligence Agent is a research-oriented agent.

Its output quality depends on its ability to discover, retrieve, and verify current information.

This document defines the capabilities required for reliable live research.

---

## 1. Web Search

### Purpose

Discover recent AI developments.

### Required capabilities

The research environment should support:

- web search
- keyword search
- date-aware search
- recent-news discovery
- search result metadata
- source URLs
- multiple search queries
- discovery across different source types

### Why it matters

The agent's daily briefing depends on finding developments from the previous 24–72 hours.

Without web search, the agent cannot reliably perform current research.

---

## 2. URL / Page Retrieval

### Purpose

Open and inspect the original source behind a discovered story.

### Required capabilities

The research environment should support:

- opening URLs
- reading webpage content
- retrieving official announcements
- retrieving technical documentation
- retrieving GitHub repository pages
- retrieving research papers
- verifying publication dates
- extracting relevant technical details

### Why it matters

Search results alone are not sufficient for verification.

The agent should inspect the underlying source whenever possible.

---

## 3. Research Paper Search

### Purpose

Discover recent AI research.

### Useful sources

Examples include:

- arXiv
- conference publications
- research lab publications
- university research pages
- official paper repositories

### Required information

For important papers the agent should be able to retrieve:

- title
- authors
- organization
- publication date
- abstract
- methodology
- results
- benchmark
- limitations
- paper URL
- code URL when available

---

## 4. GitHub Search

### Purpose

Discover new AI engineering tools and implementations.

### Required capabilities

The environment should support:

- repository search
- repository page retrieval
- README retrieval
- release information
- documentation retrieval
- issue/discussion discovery when relevant
- repository URL verification
- stars/forks retrieval when available

### Important rule

Do not invent:

- repository names
- repository URLs
- star counts
- fork counts
- release information

Only report information that was actually verified.

---

## 5. News / RSS / Industry Sources

### Purpose

Discover recent industry developments and independent reporting.

Useful sources include:

- Reuters
- Bloomberg
- Financial Times
- MIT Technology Review
- TechCrunch
- The Verge
- Ars Technica
- Wired

Primary sources should still be preferred whenever available.

---

## 6. Source Verification

Research capabilities should allow the agent to determine:

- publication date
- source identity
- original URL
- whether the information is current
- whether the development is new
- whether a report refers to an older event
- whether the claim is supported by a primary source

---

## 7. Source Classification

Each source should be treated according to its reliability and role.

### Tier 1

Primary sources:

- company announcements
- research papers
- official documentation
- official GitHub repositories
- research labs
- government/standards organizations

### Tier 2

Established independent reporting:

- Reuters
- Bloomberg
- Financial Times
- MIT Technology Review
- TechCrunch
- The Verge
- Ars Technica
- Wired

### Tier 3

Community sources:

- GitHub discussions
- Hacker News
- Reddit
- developer forums
- technical blogs

Tier 3 sources should primarily be treated as discovery leads.

---

## 8. Research Failure Behavior

If the environment does not provide live research capabilities:

The agent MUST NOT:

- invent current news
- invent sources
- fabricate URLs
- pretend that research was performed
- use old model knowledge as current news
- produce fake citations

Instead, the agent should clearly state:

> Live research could not be completed because the required source-retrieval capability is unavailable in the current execution environment.

The agent may explain which capability is missing when known.

---

## 9. Minimum Viable Research Environment

A minimum viable environment should provide:

```text
Web Search
    ↓
Source Retrieval
    ↓
Primary Source Verification
    ↓
Research Paper Discovery
    ↓
GitHub Discovery
    ↓
Synthesis
    ↓
AI Intelligence Briefing