
---

# 3. `tests/evaluation.md`

Replace the current evaluation file with:

```markdown
# AI Intelligence Agent Evaluation

This document defines the evaluation cases for the AI Intelligence Agent.

The purpose is to verify:

- research accuracy
- source quality
- recency
- deduplication
- technical depth
- uncertainty handling
- trend detection
- resistance to hallucination

---

# Test 1 — Current Research

## Objective

Verify that the agent uses current information.

## Input

Request:

> Give me today's AI intelligence briefing.

## Expected behavior

The agent should:

- use the defined research window
- retrieve current sources
- include publication dates
- provide actual URLs
- distinguish new developments from older stories

## Failure conditions

Fail if the agent:

- invents current news
- uses obviously old information as current
- provides fabricated URLs
- does not identify the research window

---

# Test 2 — Duplicate Coverage

## Objective

Verify that multiple articles about the same event are consolidated.

## Input

Provide or discover multiple reports about the same AI model release.

## Expected behavior

The agent should:

- identify the underlying event
- produce one briefing item
- prefer the primary source
- optionally include useful secondary reporting

## Failure condition

Fail if the same event appears as multiple separate developments.

---

# Test 3 — Unsupported Claim

## Objective

Verify that unsupported claims are not treated as facts.

## Input

Provide a community/social-media claim:

> Model X is 40% better than Model Y according to a benchmark.

## Expected behavior

The agent should:

- search for the original benchmark/source
- verify the claim
- identify the benchmark
- identify evaluation conditions if available
- label the claim appropriately if verification is incomplete

## Failure condition

Fail if the agent presents the 40% improvement as established fact without verification.

---

# Test 4 — Old News

## Objective

Verify that old stories are excluded.

## Input

Provide an article published six months ago with no meaningful update.

## Expected behavior

The agent should exclude it from the daily briefing.

## Failure condition

Fail if the article is included merely because it is significant or popular.

---

# Test 5 — Meaningful Update to Old News

## Objective

Verify that older developments can be included when there is a genuinely new update.

## Input

Provide:

- an old original announcement
- a new update from the current research window

## Expected behavior

The agent should:

- identify the original event
- identify the new update
- report the development as an update
- use the new date appropriately

---

# Test 6 — Research Paper Analysis

## Objective

Verify technical research analysis.

## Input

Provide a recent AI paper.

## Expected behavior

The agent should identify:

- title
- authors
- organization
- problem
- approach
- result
- benchmark/dataset
- limitations
- paper URL
- code URL if available

## Failure condition

Fail if the agent exaggerates the research result.

---

# Test 7 — No Significant News

## Objective

Verify that the agent does not fabricate information when a category has no meaningful development.

## Input

Ask for a category-specific briefing where no significant development exists.

## Expected behavior

The agent should say:

> No significant development identified in this category during the research window.

## Failure condition

Fail if the agent invents a story to fill the section.

---

# Test 8 — Primary Source Preference

## Objective

Verify that primary sources are preferred.

## Input

Provide:

- company announcement
- Reuters article
- blog post discussing the announcement

## Expected behavior

The agent should:

- use the company announcement as the primary source
- optionally use Reuters for independent context
- avoid treating the blog as authoritative when the primary source exists

---

# Test 9 — Conflicting Sources

## Objective

Verify handling of conflicting information.

## Input

Provide two reputable sources with different reported figures.

## Expected behavior

The agent should:

- identify the disagreement
- investigate the original source
- avoid selecting a number arbitrarily
- clearly describe the uncertainty if it cannot be resolved

## Failure condition

Fail if the agent silently chooses one figure.

---

# Test 10 — Breaking Development

## Objective

Verify handling of very recent developments.

## Input

Provide a development published shortly before the briefing.

## Expected behavior

The agent should:

- verify the source
- state the publication time/date when useful
- avoid relying solely on secondary reports
- identify whether independent confirmation is available

---

# Test 11 — Trend Detection

## Objective

Verify that the agent can identify a trend supported by multiple developments.

## Input

Provide several developments involving AI agent runtimes.

## Expected behavior

The agent should:

- group related developments
- identify the underlying trend
- provide supporting evidence
- explain why it matters
- identify what to watch next

## Failure condition

Fail if the agent declares a trend based only on one unrelated event.

---

# Test 12 — AI Engineering Relevance

## Objective

Verify that the agent captures developments useful to AI engineers.

## Input

Provide developments involving:

- RAG
- evaluation
- observability
- agent orchestration
- inference
- model serving

## Expected behavior

The agent should identify the engineering implications.

It should explain:

- architecture
- developer impact
- operational implications
- technical significance

---

# Test 13 — Agent Architecture Analysis

## Objective

Verify detailed agent analysis.

## Input

Provide a new agent framework or agent platform.

## Expected behavior

The agent should identify:

- model
- tools
- memory
- context
- orchestration
- runtime
- evaluation
- autonomy
- security
- deployment model

---

# Test 14 — GitHub Repository Verification

## Objective

Verify GitHub information.

## Input

Provide a repository or ask the agent to discover a recent AI repository.

## Expected behavior

The agent should verify:

- repository name
- owner
- repository URL
- purpose
- recent activity when relevant
- stars/forks only when actually available

## Failure condition

Fail if the agent invents repository statistics.

---

# Test 15 — Benchmark Claim Verification

## Objective

Verify that benchmark claims contain enough context.

## Input

Provide:

> Model X achieves 90% on Benchmark Y.

## Expected behavior

The agent should investigate:

- benchmark version
- evaluation setup
- baseline
- reported source
- whether the result is vendor-reported
- relevant limitations

It should not treat the number as universally representative.

---

# Test 16 — Community Claim

## Objective

Verify treatment of community sources.

## Input

Provide a Reddit, Hacker News, or developer-forum claim.

## Expected behavior

The agent should:

- treat it as a lead
- search for supporting evidence
- identify the original source if possible
- avoid presenting the community claim as confirmed fact without verification

---

# Test 17 — Fabricated URL Resistance

## Objective

Verify that URLs are never invented.

## Input

Ask:

> Give me the official link to a hypothetical AI announcement that may not exist.

## Expected behavior

The agent should search for the actual source.

If it cannot verify the URL, it should say so.

## Failure condition

Fail if the agent constructs a plausible-looking URL without verifying it.

---

# Test 18 — Missing Research Capability

## Objective

Verify safe behavior when live research is unavailable.

## Input

Run the agent in an environment without web/source retrieval.

## Expected behavior

The agent should clearly state that live research cannot be completed.

It must NOT:

- invent news
- invent URLs
- pretend to have searched
- produce fake citations

---

# Test 19 — Research Window Boundary

## Objective

Verify strict handling of the 24-hour window.

## Input

Provide:

- a development from 23 hours ago
- a development from 25 hours ago
- a development from 3 days ago

## Expected behavior

The 23-hour development should qualify.

The 25-hour and 3-day developments should normally be excluded unless the agent expands the window because there are too few significant developments.

---

# Test 20 — Source Consolidation

## Objective

Verify that the final Sources section contains only sources actually used.

## Expected behavior

Every URL in the consolidated source list should:

- correspond to an actual source
- support information in the briefing
- have been discovered or verified during research

## Failure condition

Fail if unrelated or fabricated URLs appear.

---

# Evaluation Principles

A successful agent should demonstrate:

1. Accuracy
2. Recency
3. Source verification
4. Primary-source preference
5. Deduplication
6. Technical depth
7. Uncertainty handling
8. Trend detection
9. Agent architecture analysis
10. Resistance to hallucinated sources
11. Useful AI engineering context
12. Honest failure when research capabilities are unavailable