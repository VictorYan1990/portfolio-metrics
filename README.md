# Portfolio Metrics API

A FastAPI-based REST API for managing investment portfolios and calculating financial metrics.

## Features

- **Portfolio Management**: Create, read, update, and delete investment portfolios
- **Financial Metrics**: Calculate key performance indicators including:
  - Total Return
  - Annualized Return
  - Volatility
  - Sharpe Ratio
  - Maximum Drawdown
- **RESTful API**: Clean, documented API endpoints
- **Modern Python**: Built with FastAPI, Pydantic, and modern Python features

## Project Structure

```
portfolio-metrics/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── .env                   # Environment variables (create this)
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py      # Application configuration
│   └── routers/
│       ├── __init__.py
│       ├── portfolio.py   # Portfolio management endpoints
│       └── metrics.py     # Financial metrics endpoints
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio-metrics
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create environment file**
   ```bash
   # Create .env file with your configuration
   cp .env.example .env
   # Edit .env with your settings
   ```

## Running the Application

### Development Server
```bash
python main.py
```

### Production Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)
- **OpenAPI Schema**: `http://localhost:8000/api/v1/openapi.json`

## API Endpoints

### Portfolios
- `GET /api/v1/portfolio/` - List all portfolios
- `GET /api/v1/portfolio/{id}` - Get specific portfolio
- `POST /api/v1/portfolio/` - Create new portfolio
- `PUT /api/v1/portfolio/{id}` - Update portfolio
- `DELETE /api/v1/portfolio/{id}` - Delete portfolio

### Metrics
- `GET /api/v1/metrics/` - List all metrics
- `GET /api/v1/metrics/{id}` - Get specific metric
- `POST /api/v1/metrics/` - Create new metric
- `GET /api/v1/metrics/portfolio/{id}/summary` - Get portfolio performance summary
- `DELETE /api/v1/metrics/{id}` - Delete metric

## Example Usage

### Create a Portfolio
```bash
curl -X POST "http://localhost:8000/api/v1/portfolio/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Investment Portfolio",
       "description": "A diversified investment portfolio",
       "initial_balance": 10000.00
     }'
```

### Add Metrics
```bash
curl -X POST "http://localhost:8000/api/v1/metrics/" \
     -H "Content-Type: application/json" \
     -d '{
       "portfolio_id": 1,
       "date": "2024-01-01",
       "value": 10000.00,
       "metric_type": "portfolio_value"
     }'
```

### Get Portfolio Summary
```bash
curl "http://localhost:8000/api/v1/metrics/portfolio/1/summary"
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
# Install black if not already installed
pip install black

# Format code
black .
```

## Configuration

The application uses environment variables for configuration. Create a `.env` file with:

```env
PROJECT_NAME=Portfolio Metrics API
PROJECT_VERSION=1.0.0
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./portfolio_metrics.db
ENVIRONMENT=development
DEBUG=true
```

## Future Enhancements

- Database integration with SQLAlchemy
- User authentication and authorization
- Real-time market data integration
- Advanced financial calculations
- Portfolio rebalancing recommendations
- Historical data analysis
- Export functionality (CSV, PDF reports)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
