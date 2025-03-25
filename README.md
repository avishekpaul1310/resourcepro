# ResourcePro

ResourcePro is a comprehensive resource management and project allocation system built with Django. It helps organizations efficiently allocate resources (people) to projects and tasks based on skills, availability, and project timelines.

## Features

- Resource management with skills and capacity tracking
- Project and task management with dependencies
- Visual allocation board with drag-and-drop interface
- Utilization tracking and overallocation warnings
- Dashboard with key performance indicators

## Installation

### Prerequisites
- Python 3.8+
- pip
- virtualenv (optional but recommended)

### Setup
1. Clone the repository
   ```
   git clone https://github.com/yourusername/resourcepro.git
   cd resourcepro
   ```

2. Create and activate virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run migrations
   ```
   python manage.py migrate
   ```

5. Create a superuser
   ```
   python manage.py createsuperuser
   ```

6. Run the development server
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Architecture

ResourcePro follows a modular Django architecture with the following apps:

- **accounts**: User authentication and profiles
- **resources**: Resource (people) management and skills
- **projects**: Project and task management
- **allocation**: Resource allocation to tasks
- **dashboard**: Overview and KPI visualization
- **api**: REST API endpoints for the frontend
- **core**: Shared functionality

## Testing

ResourcePro has extensive testing:

- Unit tests for models, forms, and views
- Integration tests for workflows
- End-to-end tests with Selenium
- Performance tests

### Running Tests

```
# Run all tests
python run_tests.py

# Run specific test modules
python manage.py test resources.tests
python manage.py test integration_tests
python manage.py test e2e_tests
python manage.py test performance_tests
```

## Test Coverage

The project includes several types of tests to ensure functionality:

- **Unit Tests**: Testing individual components in isolation
- **Integration Tests**: Testing interactions between components
- **E2E Tests**: Testing complete workflows with Selenium
- **Performance Tests**: Testing application responsiveness under load
- **Edge Case Tests**: Testing unusual scenarios like weekend-only tasks

## Deployment

### Production Setup
1. Set environment variables for production
   ```
   export DJANGO_SETTINGS_MODULE=resourcepro.settings.production
   export SECRET_KEY=your_secure_key
   export DATABASE_URL=your_database_url
   ```

2. Collect static files
   ```
   python manage.py collectstatic
   ```

3. Use a production-ready web server (Gunicorn, uWSGI)
   ```
   gunicorn resourcepro.wsgi:application
   ```

4. Set up a reverse proxy (Nginx, Apache)

## Project Structure

```
resourcepro/
├── accounts/            # User authentication and profiles
├── allocation/          # Resource allocation to tasks
├── api/                 # REST API endpoints
├── core/                # Shared functionality
├── dashboard/           # Overview and KPI visualization
├── e2e_tests/           # End-to-end tests with Selenium
├── integration_tests/   # Integration tests
├── performance_tests/   # Performance tests
├── projects/            # Project and task management
├── resources/           # Resource management and skills
├── resourcepro/         # Project settings
├── static/              # Static files
├── templates/           # Base templates
├── .env                 # Environment variables (example)
├── .gitignore           # Git ignore file
├── manage.py            # Django management script
├── README.md            # This file
├── requirements.txt     # Project dependencies
└── run_tests.py         # Custom test runner
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
