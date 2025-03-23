#!/bin/bash
# test_report.sh

# Set up virtual environment
source venv/bin/activate

# Run coverage for Python tests
coverage run --source='.' manage.py test

# Generate coverage report
coverage report -m
coverage html

# Run Selenium tests
SELENIUM_TESTS=true python run_tests.py

# Generate a timestamp for the report
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="test_report_$TIMESTAMP.txt"

# Create test report header
echo "ResourcePro Test Report - $TIMESTAMP" > $REPORT_FILE
echo "====================================" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Add coverage data to report
echo "Code Coverage Summary:" >> $REPORT_FILE
coverage report -m >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Add model information
echo "Database Model Stats:" >> $REPORT_FILE
echo "---------------------" >> $REPORT_FILE
python manage.py inspectdb | grep "class" | wc -l | xargs -I {} echo "Total models: {}" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Add view information
echo "View Stats:" >> $REPORT_FILE
echo "----------" >> $REPORT_FILE
find . -name "views.py" -exec grep -l "def " {} \; | xargs grep -l "def " | wc -l | xargs -I {} echo "Total view files: {}" >> $REPORT_FILE
find . -name "views.py" -exec grep "def " {} \; | wc -l | xargs -I {} echo "Total view functions: {}" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Add template information
echo "Template Stats:" >> $REPORT_FILE
echo "--------------" >> $REPORT_FILE
find . -name "*.html" | wc -l | xargs -I {} echo "Total templates: {}" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# Print summary
echo "Test Report generated: $REPORT_FILE"

# Open HTML coverage report
python -m webbrowser "htmlcov/index.html"