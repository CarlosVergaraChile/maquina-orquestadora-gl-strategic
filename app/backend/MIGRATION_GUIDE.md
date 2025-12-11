# Database Migration Guide - Máquina Orquestadora

## Overview

This guide covers database schema migrations using Alembic for the Máquina Orquestadora system.

## Setup

### Prerequisites
- Python 3.9+
- SQLAlchemy 2.0+
- Alembic 1.13+

### Installation

```bash
pip install sqlalchemy==2.0.23 alembic==1.13.0
```

## Migration Workflow

### Creating New Migrations

1. **Auto-generate migration** from model changes:
```bash
alembic revision --autogenerate -m "Description of changes"
```

2. **Manual migration** for complex changes:
```bash
alembic revision -m "Custom migration description"
```

3. **Edit** the generated file in `alembic/versions/`

### Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade 001

# Downgrade to previous version
alembic downgrade -1
```

## Current Schema

### Tables

**orchestration_contexts**
- `id`: UUID primary key
- `name`: Unique context name
- `description`: Optional description
- `created_at`, `updated_at`: Timestamps

**decisions**
- `id`: UUID primary key
- `context_id`: FK to orchestration_contexts
- `decision_type`: Type classification
- `metadata`: JSON field for extensibility
- `created_at`: Timestamp

**model_responses**
- `id`: UUID primary key
- `decision_id`: FK to decisions
- `model_name`: Model identifier
- `response_text`: Generated response
- `confidence_score`: 0.0-1.0 score
- `created_at`: Timestamp

**human_feedback**
- `id`: UUID primary key
- `decision_id`: FK to decisions
- `feedback_text`: Human feedback
- `rating`: 1-5 rating scale
- `created_at`: Timestamp

## Best Practices

1. **Always test migrations locally** before deploying
2. **Keep migrations small** and focused
3. **Use descriptive** migration names
4. **Never modify** already-applied migrations
5. **Back up** production database before migrations
6. **Review** auto-generated migrations for accuracy

## Troubleshooting

### Migration conflicts
```bash
alembic heads  # Show migration heads
alembic branches  # Show branches
alembic merge  # Merge conflicting heads
```

### Reset migrations (Development only)
```bash
rm alembic/versions/*.py
rm orchestrator.db
alembic stamp head
```
