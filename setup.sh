#!/bin/bash

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Set up PostgreSQL with PgVector
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16

echo "Environment setup complete!"