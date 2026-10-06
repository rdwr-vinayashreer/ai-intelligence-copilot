# AI Intelligence Agent Evaluation

## Purpose

This document defines the evaluation framework for the AI Intelligence Agent.

The evaluation has two complementary layers:

1. **Behavioral evaluation** — verifies that the intelligence agent researches,
   verifies, analyzes, and presents information correctly.
2. **Operational evaluation** — measures the quality and reliability of each
   production run.

The behavioral tests validate the intelligence itself.

The operational metrics validate whether a generated briefing is complete,
fresh, source-backed, and successfully delivered.

---

# 1. Evaluation Architecture

Each intelligence run should be associated with a unique `run_id`.

```text
AI Intelligence Run
        |
        +-- run_id
        +-- profile
        +-- research window
        |
        v
     Research
        |
        v
     Briefing
        |
        v
   Quality Evaluation
        |
        +-- Source coverage
        +-- Primary-source rate
        +-- Verification integrity
        +-- Freshness
        +-- Duplicate rate
        +-- Completeness
        +-- Runtime
        |
        v
     Delivery
        |
        v
 Evaluation Artifact