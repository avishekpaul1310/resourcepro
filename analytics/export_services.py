import io
import pandas as pd
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from django.db import models
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from .services import UtilizationTrackingService, CostTrackingService
from .models import ResourceDemandForecast, SkillDemandAnalysis
from resources.models import Resource
from projects.models import Project

class ReportExportService:
    """Service for exporting reports to PDF and Excel formats"""
    
    def export_utilization_pdf(self):
        """Export utilization report as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Title
        title = Paragraph("Resource Utilization Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = timezone.now().strftime("%B %d, %Y")
        metadata = Paragraph(f"Generated on: {report_date}", styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Get utilization data
        utilization_service = UtilizationTrackingService()
        resources = Resource.objects.all()
        
        # Create table data
        table_data = [['Resource', 'Role', 'Current Utilization', 'Avg 30-day Utilization', 'Status']]
        
        for resource in resources:
            current_util = resource.current_utilization()
            trends = utilization_service.get_utilization_trends(resource, 30)
            avg_util = trends.aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
            
            if current_util > 100:
                status = "Over-allocated"
            elif current_util > 85:
                status = "High utilization"
            else:
                status = "Normal"
            
            table_data.append([
                resource.name,
                resource.role,
                f"{current_util:.1f}%",
                f"{avg_util:.1f}%",
                status
            ])
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="utilization_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_utilization_excel(self):
        """Export utilization report as Excel"""
        # Get data
        utilization_service = UtilizationTrackingService()
        resources = Resource.objects.all()
        
        data = []
        for resource in resources:
            current_util = resource.current_utilization()
            trends = utilization_service.get_utilization_trends(resource, 30)
            avg_util = trends.aggregate(avg=models.Avg('utilization_percentage'))['avg'] or 0
            
            data.append({
                'Resource': resource.name,
                'Role': resource.role,
                'Current Utilization (%)': current_util,
                'Avg 30-day Utilization (%)': avg_util,
                'Capacity (hrs/week)': resource.capacity,
                'Cost per Hour': float(resource.cost_per_hour)
            })
        
        # Create DataFrame and Excel file
        df = pd.DataFrame(data)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Utilization Report', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Utilization Report']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="utilization_report_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
    
    def export_cost_pdf(self):
        """Export cost tracking report as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        
        # Title
        title = Paragraph("Project Cost Tracking Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = timezone.now().strftime("%B %d, %Y")
        metadata = Paragraph(f"Generated on: {report_date}", styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Get cost data
        cost_service = CostTrackingService()
        cost_report = cost_service.get_cost_variance_report()
        
        # Create table data
        table_data = [['Project', 'Budget', 'Estimated Cost', 'Actual Cost', 'Variance', 'Status']]
        
        for item in cost_report:
            project = item['project']
            variance = item['variance']
            
            if variance < 0:
                status = "Over Budget"
            elif variance < item['estimated_cost'] * 0.1:
                status = "At Risk"
            else:
                status = "On Track"
            
            table_data.append([
                project.name,
                f"${item['budget']:.2f}" if item['budget'] else "N/A",
                f"${item['estimated_cost']:.2f}",
                f"${item['actual_cost']:.2f}",
                f"${variance:.2f}",
                status
            ])
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="cost_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_cost_excel(self):
        """Export cost tracking report as Excel"""
        cost_service = CostTrackingService()
        cost_report = cost_service.get_cost_variance_report()
        
        data = []
        for item in cost_report:
            project = item['project']
            data.append({
                'Project': project.name,
                'Budget': float(item['budget']) if item['budget'] else 0,
                'Estimated Cost': float(item['estimated_cost']),
                'Actual Cost': float(item['actual_cost']),
                'Variance': float(item['variance']),
                'Variance %': item['variance_percentage'],
                'Budget Utilization %': item['budget_utilization'],
                'Status': project.get_status_display(),
                'Start Date': project.start_date.strftime('%Y-%m-%d'),
                'End Date': project.end_date.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Cost Report', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Cost Report']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="cost_report_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
    
    def export_forecast_pdf(self):
        """Export demand forecast report as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1
        )
        
        # Title
        title = Paragraph("Resource Demand Forecast Report", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Report metadata
        report_date = timezone.now().strftime("%B %d, %Y")
        metadata = Paragraph(f"Generated on: {report_date}", styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 20))
        
        # Get forecast data
        forecasts = ResourceDemandForecast.objects.all()[:20]
        
        # Create table data
        table_data = [['Role', 'Predicted Demand (hrs)', 'Confidence', 'Forecast Period', 'Generated']]
        
        for forecast in forecasts:
            table_data.append([
                forecast.resource_role,
                f"{forecast.predicted_demand_hours:.1f}",
                f"{forecast.confidence_score:.1%}",
                f"{forecast.period_start} to {forecast.period_end}",
                forecast.forecast_date.strftime('%Y-%m-%d')
            ])
        
        # Create and style table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="forecast_report_{timezone.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    def export_forecast_excel(self):
        """Export demand forecast report as Excel"""
        forecasts = ResourceDemandForecast.objects.all()
        
        data = []
        for forecast in forecasts:
            data.append({
                'Role': forecast.resource_role,
                'Predicted Demand (hrs)': float(forecast.predicted_demand_hours),
                'Confidence Score': float(forecast.confidence_score),
                'Period Start': forecast.period_start.strftime('%Y-%m-%d'),
                'Period End': forecast.period_end.strftime('%Y-%m-%d'),
                'Forecast Date': forecast.forecast_date.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(data)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Demand Forecast', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Demand Forecast']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="forecast_report_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        
        return response
    
    def export_utilization_report_pdf(self, resource_id):
        """Export utilization report for a specific resource as PDF"""
        resource = Resource.objects.get(id=resource_id)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1
        )
        
        # Title
        title = Paragraph(f"Utilization Report - {resource.name}", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Resource info
        info_data = [
            ['Resource Name:', resource.name],
            ['Role:', resource.role],
            ['Department:', resource.department],
            ['Capacity:', f"{resource.capacity} hours/week"],
            ['Current Utilization:', f"{resource.current_utilization():.1f}%"]
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(info_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Save to file
        filename = f"reports/utilization_{resource.name.replace(' ', '_')}.pdf"
        import os
        os.makedirs('reports', exist_ok=True)
        
        with open(filename, 'wb') as f:
            f.write(buffer.getvalue())
        
        return filename
    
    def export_utilization_report_excel(self, resource_id):
        """Export utilization report for a specific resource as Excel"""
        resource = Resource.objects.get(id=resource_id)
        
        # Create DataFrame with resource data
        data = {
            'Resource Name': [resource.name],
            'Role': [resource.role],
            'Department': [resource.department],
            'Capacity (hours/week)': [resource.capacity],
            'Current Utilization (%)': [resource.current_utilization()]
        }
        
        df = pd.DataFrame(data)
        
        # Save to file
        filename = f"reports/utilization_{resource.name.replace(' ', '_')}.xlsx"
        import os
        os.makedirs('reports', exist_ok=True)
        
        df.to_excel(filename, index=False)
        return filename
    
    def export_cost_report_pdf(self):
        """Export cost report as PDF"""
        return self.export_cost_pdf()
    
    def export_cost_report_excel(self):
        """Export cost report as Excel"""
        return self.export_cost_excel()
