# User Configuration

## Purpose

The User Configuration Layer allows employees to use the AI Intelligence platform without modifying the intelligence agent or execution runtime.

## Configuration Flow

Employee -> User Configuration -> Scheduler -> Runtime -> AI Intelligence Core -> Run Contract -> Delivery

## User Configuration Owns

- user identity
- selected intelligence profile
- selected topics
- schedule
- timezone
- delivery destination

## User Configuration Does Not Own

- research instructions
- source verification rules
- model implementation
- runtime implementation
- authentication credentials

## Security

User configuration must never contain passwords, API keys, SMTP credentials, OAuth client secrets, or access tokens.

Secrets belong in the secure runtime or enterprise secret-management layer.

## Design Principle

Configure the platform; do not modify the intelligence engine.
