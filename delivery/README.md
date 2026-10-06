# Delivery Layer

The Delivery Layer is responsible for delivering completed AI Intelligence
briefings to users or systems.

## Responsibility

The delivery layer receives a completed briefing and sends it through a
configured delivery channel.

It must not:

- perform AI research
- select research topics
- verify sources
- generate the briefing
- modify intelligence profiles

## Architecture

```text
AI Intelligence Core
        |
        v
Delivery Contract
        |
   +----+----+------+
   |         |      |
 Email     Teams   Webhook