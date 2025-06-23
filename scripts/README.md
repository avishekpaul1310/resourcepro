# Utility Scripts

This directory contains utility scripts for ResourcePro setup, data population, and maintenance.

## Setup Scripts

### `create_admin.py`
Creates an admin user for the Django application.
- **Username**: admin
- **Password**: admin123
- **Email**: admin@example.com

**Usage:**
```bash
python scripts/create_admin.py
```

## Data Population Scripts

### `populate_comprehensive_data.py`
Populates the database with comprehensive test data including:
- Users and resources
- Skills and projects
- Tasks and assignments
- Time entries
- Analytics data

**Usage:**
```bash
python scripts/populate_comprehensive_data.py
```

### `populate_analytics.py`
Populates analytics data for testing reports and dashboards.
- Historical utilization data
- Cost tracking information
- Performance metrics

**Usage:**
```bash
python scripts/populate_analytics.py
```

### `populate_calendar_data.py`
Creates availability calendar data for resources.
- Availability entries
- Time-off periods
- Schedule conflicts

**Usage:**
```bash
python scripts/populate_calendar_data.py
```

## Data Generation Scripts

### `generate_all_role_forecasts.py`
Generates demand forecasts for all roles and skills in the system.
- Resource demand analysis
- Skill gap identification
- Future planning data

**Usage:**
```bash
python scripts/generate_all_role_forecasts.py
```

### `generate_more_forecasts.py`
Generates additional forecast data for testing analytics features.
- Extended forecast periods
- Multiple scenario planning
- Trend analysis data

**Usage:**
```bash
python scripts/generate_more_forecasts.py
```

## Running Scripts

All scripts should be run from the project root directory:

```bash
# From the resourcepro/ directory
python scripts/script_name.py
```

Make sure you have activated your virtual environment and installed all dependencies before running these scripts.
