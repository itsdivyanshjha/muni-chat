# Municipal AI Insights Backend

A FastAPI-based backend for the Municipal AI Insights platform that provides AI-powered analytics over municipal datasets.

## Features

- **Natural Language Queries**: Convert natural language questions into safe SQL queries
- **LLM Integration**: Uses OpenRouter API with GPT-4 for intelligent query processing
- **Data Safety**: SQL validation and read-only database access
- **Visualization**: Generates Vega-Lite chart specifications
- **Extensible Schema**: Generic warehouse design for any municipal indicator
- **Docker Ready**: Full containerization with PostgreSQL

## Architecture

### Database Schema

The system uses a star schema with:
- `fact_measure`: Main fact table for all measurements
- `dim_time`: Time dimension (year, quarter, month)
- `dim_geo`: Geography dimension (state, district, zone, ward)
- `dim_indicator`: Indicator dimension (what is being measured)

### API Endpoints

1. `POST /api/insights` - Generate insights from natural language queries
2. `GET /api/schema` - Get sanitized database schema
3. `GET /api/datasets` - List available datasets
4. `GET /healthz` - Health check

### Security Features

- Read-only database role for runtime queries
- SQL injection protection via parameterized queries
- Forbidden keyword detection (INSERT, UPDATE, DELETE, etc.)
- Query timeout and row limits
- Table access whitelist

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key

### 1. Environment Setup

Copy the environment template:
```bash
cp env.example .env
```

Edit `.env` and set your OpenRouter API key:
```bash
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 2. Start the Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- FastAPI backend on port 8000

### 3. Run Migrations

```bash
# Install dependencies locally (optional, for development)
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create seed data
python seed_data.py
```

### 4. Test the API

Health check:
```bash
curl http://localhost:8000/healthz
```

Get schema:
```bash
curl http://localhost:8000/api/schema
```

Generate insights:
```bash
curl -X POST "http://localhost:8000/api/insights" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me forest cover trends in Ranchi from 2019 to 2021",
    "filters": {
      "time": {"from": "2019-01-01", "to": "2021-12-31"},
      "place": {"district": "Ranchi"}
    }
  }'
```

## Development

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your local database and update `.env` accordingly

3. Run the development server:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
pytest tests/ -v
```

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | Required |
| `MODEL_SLUG` | LLM model to use | `openai/gpt-4` |
| `DATABASE_URL` | Owner database connection | Required |
| `RUNTIME_DB_URL` | Read-only database connection | Required |
| `APP_ENV` | Environment (dev/prod) | `dev` |
| `DEBUG` | Enable debug logging | `true` |
| `QUERY_TIMEOUT_SECONDS` | SQL query timeout | `10` |
| `MAX_ROWS_RETURNED` | Max rows from database | `5000` |
| `MAX_PREVIEW_ROWS` | Max rows in API response | `50` |

### Database Roles

The system uses two database roles:
- `app_owner`: For migrations and ETL (full permissions)
- `app_readonly`: For runtime queries (read-only)

## Adding New Datasets

The platform is designed to be extensible. To add new datasets:

1. **Prepare Data**: Format your data with indicator, geography, and time dimensions
2. **Insert Indicators**: Add new entries to `dim_indicator` table
3. **Insert Geography**: Add new geographic entities to `dim_geo` if needed
4. **Insert Time**: Add time periods to `dim_time` if needed
5. **Load Facts**: Insert measurements into `fact_measure`

### Example ETL Script

```python
# Example: Loading water quality data
indicator = DimIndicator(
    slug="water_quality_index",
    title="Water Quality Index",
    unit="index",
    category="Environment",
    description="Water quality measurement index",
    default_agg="AVG"
)

# Insert measurements for each location/time combination
measurement = FactMeasure(
    indicator_id=indicator.id,
    geo_id=location.id,
    time_id=time_period.id,
    value=75.5,
    quality_flag="verified"
)
```

## API Response Format

### Insights Response

```json
{
  "insight_text": "Conversational analysis of the data",
  "sql_used": "SELECT statement that was executed",
  "data_preview": {
    "columns": ["column1", "column2"],
    "rows": [["value1", "value2"]]
  },
  "viz": {
    "type": "vega-lite",
    "spec": {
      "mark": "line",
      "encoding": {...}
    }
  },
  "doc_citations": [
    {
      "title": "Source Document",
      "url": "https://example.com",
      "excerpt": "Relevant excerpt"
    }
  ],
  "filters_applied": {
    "time": {"from": "2019-01-01", "to": "2021-12-31"},
    "place": {"district": "Ranchi"},
    "extra": {}
  },
  "disclaimers": ["Any relevant disclaimers"]
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check that PostgreSQL is running
   - Verify connection strings in `.env`
   - Ensure database roles exist

2. **OpenRouter API Errors**
   - Verify API key is correct
   - Check API quota and billing
   - Review model slug spelling

3. **SQL Guard Errors**
   - Ensure queries only use SELECT/WITH
   - Check table names are in whitelist
   - Verify no forbidden keywords

### Logs

View application logs:
```bash
docker-compose logs backend
```

View database logs:
```bash
docker-compose logs db
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Your license here]
