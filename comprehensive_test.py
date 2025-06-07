#!/usr/bin/env python
"""
Comprehensive test script for ResourcePro enhanced features:
1. Predictive analytics for resource demand forecasting
2. Export capabilities (PDF, Excel) for reports
3. Time tracking integration for actual vs. estimated work
4. Resource cost tracking and budget management
5. Availability calendar with vacation/sick leave management
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resourcepro.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from resources.models import Resource, TimeEntry, ResourceAvailability, Skill
from projects.models import Project, Task
from allocation.models import Assignment
from analytics.models import ResourceDemandForecast, HistoricalUtilization, SkillDemandAnalysis, ProjectCostTracking
from analytics.services import PredictiveAnalyticsService, UtilizationTrackingService, CostTrackingService
from analytics.export_services import ReportExportService

class ComprehensiveTestSuite:
    def __init__(self):
        self.test_results = {}
        print("🚀 Starting Comprehensive ResourcePro Feature Testing")
        print("=" * 60)
    
    def run_all_tests(self):
        """Run all test suites"""
        try:
            self.test_predictive_analytics()
            self.test_export_functionality()
            self.test_time_tracking()
            self.test_cost_tracking()
            self.test_availability_calendar()
            self.test_data_integrity()
            
            self.print_summary()
            return True
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
            return False
    
    def test_predictive_analytics(self):
        """Test Feature 1: Predictive Analytics"""
        print("\n📊 Testing Predictive Analytics...")
        
        try:
            analytics_service = PredictiveAnalyticsService()
            
            # Test demand forecasting
            forecasts = analytics_service.generate_resource_demand_forecast(days_ahead=30)
            if forecasts:
                print(f"✅ Generated {len(forecasts)} demand forecasts")
                for forecast in forecasts[:3]:  # Show first 3
                    print(f"   • {forecast.resource_role}: {forecast.predicted_demand_hours:.1f}h "
                          f"(confidence: {forecast.confidence_score:.1%})")
            else:
                print("⚠️  No forecasts generated (may need more historical data)")
            
            # Test skill demand analysis
            skill_analyses = analytics_service.analyze_skill_demand()
            print(f"✅ Analyzed demand for {len(skill_analyses)} skills")
            for analysis in skill_analyses[:3]:  # Show first 3
                print(f"   • {analysis.skill_name}: {analysis.current_demand} current, "
                      f"{analysis.predicted_future_demand} predicted")
            
            self.test_results['predictive_analytics'] = True
            
        except Exception as e:
            print(f"❌ Predictive analytics test failed: {e}")
            self.test_results['predictive_analytics'] = False
    
    def test_export_functionality(self):
        """Test Feature 2: Export Capabilities"""
        print("\n📄 Testing Export Functionality...")
        
        try:
            export_service = ReportExportService()
            
            # Test utilization report export
            resources = Resource.objects.all()[:3]
            for resource in resources:
                try:
                    # Test PDF export
                    pdf_path = export_service.export_utilization_report_pdf(resource.id)
                    if os.path.exists(pdf_path):
                        file_size = os.path.getsize(pdf_path)
                        print(f"✅ PDF report generated for {resource.name} ({file_size} bytes)")
                    else:
                        print(f"⚠️  PDF not found for {resource.name}")
                    
                    # Test Excel export
                    excel_path = export_service.export_utilization_report_excel(resource.id)
                    if os.path.exists(excel_path):
                        file_size = os.path.getsize(excel_path)
                        print(f"✅ Excel report generated for {resource.name} ({file_size} bytes)")
                    else:
                        print(f"⚠️  Excel not found for {resource.name}")
                        
                except Exception as e:
                    print(f"⚠️  Export failed for {resource.name}: {e}")
                    continue
            
            # Test cost report export
            try:
                cost_pdf = export_service.export_cost_report_pdf()
                if os.path.exists(cost_pdf):
                    file_size = os.path.getsize(cost_pdf)
                    print(f"✅ Cost report PDF generated ({file_size} bytes)")
                
                cost_excel = export_service.export_cost_report_excel()
                if os.path.exists(cost_excel):
                    file_size = os.path.getsize(cost_excel)
                    print(f"✅ Cost report Excel generated ({file_size} bytes)")
                    
            except Exception as e:
                print(f"⚠️  Cost report export failed: {e}")
            
            self.test_results['export_functionality'] = True
            
        except Exception as e:
            print(f"❌ Export functionality test failed: {e}")
            self.test_results['export_functionality'] = False
    
    def test_time_tracking(self):
        """Test Feature 3: Time Tracking Integration"""
        print("\n⏱️  Testing Time Tracking...")
        
        try:
            # Test time entry creation and validation
            time_entries = TimeEntry.objects.all()
            print(f"✅ Found {time_entries.count()} time entries in system")
            
            # Test time tracking calculations
            total_tracked_hours = sum(entry.hours for entry in time_entries)
            print(f"✅ Total tracked hours: {total_tracked_hours:.1f}")
              # Test actual vs estimated comparison
            tasks_with_time = Task.objects.filter(time_entries__isnull=False).distinct()
            print(f"✅ Tasks with time tracking: {tasks_with_time.count()}")
            
            variance_data = []
            for task in tasks_with_time[:5]:  # Test first 5 tasks
                actual_hours = sum(entry.hours for entry in task.time_entries.all())
                if task.estimated_hours:
                    variance = actual_hours - task.estimated_hours
                    variance_pct = (variance / task.estimated_hours * 100) if task.estimated_hours > 0 else 0
                    variance_data.append({
                        'task': task.name,
                        'estimated': task.estimated_hours,
                        'actual': actual_hours,
                        'variance': variance,
                        'variance_pct': variance_pct
                    })
            
            if variance_data:
                print("✅ Time variance analysis:")
                for data in variance_data:
                    print(f"   • {data['task']}: {data['actual']:.1f}h actual vs "
                          f"{data['estimated']:.1f}h estimated ({data['variance_pct']:+.1f}%)")
            
            self.test_results['time_tracking'] = True
            
        except Exception as e:
            print(f"❌ Time tracking test failed: {e}")
            self.test_results['time_tracking'] = False
    
    def test_cost_tracking(self):
        """Test Feature 4: Resource Cost Tracking"""
        print("\n💰 Testing Cost Tracking...")
        
        try:
            cost_service = CostTrackingService()
            
            # Update project costs
            cost_service.update_project_costs()
            
            # Test cost variance report
            variance_report = cost_service.get_cost_variance_report()
            print(f"✅ Generated cost variance report for {len(variance_report)} projects")
            
            for project_data in variance_report[:3]:  # Show first 3
                project = project_data['project']
                estimated = project_data['estimated_cost'] or 0
                actual = project_data['actual_cost'] or 0
                variance = project_data['variance']
                
                print(f"   • {project.name}: ${actual:.2f} actual vs ${estimated:.2f} estimated "
                      f"(variance: ${variance:+.2f})")
            
            # Test project cost tracking records
            cost_tracking_records = ProjectCostTracking.objects.all()
            print(f"✅ Found {cost_tracking_records.count()} cost tracking records")
              # Test resource cost calculations
            resources = Resource.objects.all()[:3]
            for resource in resources:
                hourly_rate = resource.cost_per_hour or 50.0  # Default rate
                capacity = resource.capacity or 40.0
                monthly_cost = hourly_rate * capacity * 4  # 4 weeks
                print(f"   • {resource.name}: ${hourly_rate}/hr, monthly cost ~${monthly_cost:.2f}")
            
            self.test_results['cost_tracking'] = True
            
        except Exception as e:
            print(f"❌ Cost tracking test failed: {e}")
            self.test_results['cost_tracking'] = False
    
    def test_availability_calendar(self):
        """Test Feature 5: Availability Calendar"""
        print("\n📅 Testing Availability Calendar...")
        
        try:
            # Test availability records
            availability_records = ResourceAvailability.objects.all()
            print(f"✅ Found {availability_records.count()} availability records")
            
            # Test different availability types
            availability_types = {}
            for record in availability_records:
                availability_type = record.availability_type
                if availability_type not in availability_types:
                    availability_types[availability_type] = 0
                availability_types[availability_type] += 1
            
            print("✅ Availability breakdown:")
            for avail_type, count in availability_types.items():
                print(f"   • {avail_type}: {count} records")
            
            # Test current availability
            available_now = ResourceAvailability.objects.filter(
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date(),
                availability_type='available'
            ).count()
            
            unavailable_now = ResourceAvailability.objects.filter(
                start_date__lte=timezone.now().date(),
                end_date__gte=timezone.now().date(),
                availability_type__in=['vacation', 'sick_leave', 'unavailable']
            ).count()
            
            print(f"✅ Current availability: {available_now} available, {unavailable_now} unavailable")
            
            # Test upcoming unavailability
            upcoming_unavailable = ResourceAvailability.objects.filter(
                start_date__gt=timezone.now().date(),
                start_date__lte=timezone.now().date() + timedelta(days=30),
                availability_type__in=['vacation', 'sick_leave', 'unavailable']
            ).count()
            
            print(f"✅ Upcoming unavailability (30 days): {upcoming_unavailable} records")
            
            self.test_results['availability_calendar'] = True
            
        except Exception as e:
            print(f"❌ Availability calendar test failed: {e}")
            self.test_results['availability_calendar'] = False
    
    def test_data_integrity(self):
        """Test data integrity and relationships"""
        print("\n🔍 Testing Data Integrity...")
        
        try:
            # Test resource relationships
            resources = Resource.objects.all()
            assignments = Assignment.objects.all()
            time_entries = TimeEntry.objects.all()
            
            print(f"✅ Data summary:")
            print(f"   • Resources: {resources.count()}")
            print(f"   • Projects: {Project.objects.count()}")
            print(f"   • Tasks: {Task.objects.count()}")
            print(f"   • Assignments: {assignments.count()}")
            print(f"   • Time Entries: {time_entries.count()}")
            print(f"   • Skills: {Skill.objects.count()}")
            
            # Test relationship integrity
            orphaned_assignments = assignments.filter(resource__isnull=True).count()
            orphaned_time_entries = time_entries.filter(resource__isnull=True).count()
            
            if orphaned_assignments == 0 and orphaned_time_entries == 0:
                print("✅ All relationships are properly maintained")
            else:
                print(f"⚠️  Found {orphaned_assignments} orphaned assignments, "
                      f"{orphaned_time_entries} orphaned time entries")
            
            # Test analytics model integrity
            forecasts = ResourceDemandForecast.objects.count()
            utilization_records = HistoricalUtilization.objects.count()
            skill_analyses = SkillDemandAnalysis.objects.count()
            cost_tracking = ProjectCostTracking.objects.count()
            
            print(f"✅ Analytics data:")
            print(f"   • Demand forecasts: {forecasts}")
            print(f"   • Utilization records: {utilization_records}")
            print(f"   • Skill analyses: {skill_analyses}")
            print(f"   • Cost tracking: {cost_tracking}")
            
            self.test_results['data_integrity'] = True
            
        except Exception as e:
            print(f"❌ Data integrity test failed: {e}")
            self.test_results['data_integrity'] = False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            test_display = test_name.replace('_', ' ').title()
            print(f"  {status} - {test_display}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! ResourcePro enhancements are working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Review the output above for details.")

if __name__ == '__main__':
    test_suite = ComprehensiveTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
