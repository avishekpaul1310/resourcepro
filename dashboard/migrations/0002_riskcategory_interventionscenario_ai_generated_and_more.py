# Generated by Django 4.2.6 on 2025-06-22 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_alter_project_options_project_budget'),
        ('resources', '0005_add_remote_worker_fields'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('risk_type', models.CharField(choices=[('resource', 'Resource & Allocation'), ('technical', 'Technical & Quality'), ('external', 'External Dependencies'), ('team', 'Team Dynamics'), ('business', 'Business & Strategic'), ('operational', 'Operational'), ('financial', 'Financial & Budget'), ('timeline', 'Schedule & Timeline'), ('scope', 'Scope & Requirements'), ('quality', 'Quality & Standards')], max_length=20)),
                ('description', models.TextField()),
                ('severity_weight', models.FloatField(default=1.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='ai_generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='custom_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='custom_intervention_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='intervention_type',
            field=models.CharField(choices=[('reassignment', 'Task Reassignment'), ('overtime', 'Overtime Authorization'), ('resource_addition', 'Additional Resource'), ('deadline_extension', 'Deadline Extension'), ('scope_reduction', 'Scope Reduction'), ('training', 'Training & Skill Development'), ('process_improvement', 'Process Optimization'), ('external_resource', 'External Consultant/Contractor'), ('technology_upgrade', 'Technology/Tool Upgrade'), ('risk_mitigation', 'Risk Mitigation Plan'), ('communication_plan', 'Communication Enhancement'), ('quality_assurance', 'Quality Assurance Boost'), ('stakeholder_engagement', 'Stakeholder Re-engagement'), ('custom', 'Custom Intervention')], default='reassignment', max_length=30),
        ),
        migrations.AlterField(
            model_name='interventionscenario',
            name='scenario_type',
            field=models.CharField(choices=[('reassignment', 'Task Reassignment'), ('overtime', 'Overtime Authorization'), ('resource_addition', 'Additional Resource'), ('deadline_extension', 'Deadline Extension'), ('scope_reduction', 'Scope Reduction'), ('training', 'Training & Skill Development'), ('process_improvement', 'Process Optimization'), ('external_resource', 'External Consultant/Contractor'), ('technology_upgrade', 'Technology/Tool Upgrade'), ('risk_mitigation', 'Risk Mitigation Plan'), ('communication_plan', 'Communication Enhancement'), ('quality_assurance', 'Quality Assurance Boost'), ('stakeholder_engagement', 'Stakeholder Re-engagement'), ('custom', 'Custom Intervention')], max_length=30),
        ),
        migrations.CreateModel(
            name='InterventionTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('intervention_type', models.CharField(choices=[('reassignment', 'Task Reassignment'), ('overtime', 'Overtime Authorization'), ('resource_addition', 'Additional Resource'), ('deadline_extension', 'Deadline Extension'), ('scope_reduction', 'Scope Reduction'), ('training', 'Training & Skill Development'), ('process_improvement', 'Process Optimization'), ('external_resource', 'External Consultant/Contractor'), ('technology_upgrade', 'Technology/Tool Upgrade'), ('risk_mitigation', 'Risk Mitigation Plan'), ('communication_plan', 'Communication Enhancement'), ('quality_assurance', 'Quality Assurance Boost'), ('stakeholder_engagement', 'Stakeholder Re-engagement'), ('custom', 'Custom Intervention')], max_length=30)),
                ('template_config', models.JSONField(default=dict)),
                ('success_conditions', models.JSONField(default=list)),
                ('resource_requirements', models.JSONField(default=dict)),
                ('average_success_rate', models.FloatField(default=0.0)),
                ('average_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('average_time_impact', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('risk_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.riskcategory')),
            ],
        ),
        migrations.CreateModel(
            name='DynamicRisk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], max_length=10)),
                ('probability', models.FloatField()),
                ('impact_score', models.FloatField()),
                ('ai_analysis', models.JSONField(default=dict)),
                ('suggested_interventions', models.JSONField(default=list)),
                ('status', models.CharField(default='identified', max_length=20)),
                ('identified_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.riskcategory')),
                ('related_project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
                ('related_resource', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='resources.resource')),
                ('related_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.task')),
            ],
            options={
                'ordering': ['-severity', '-impact_score', '-identified_at'],
            },
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='dynamic_risk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.dynamicrisk'),
        ),
        migrations.AddField(
            model_name='interventionscenario',
            name='risk_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.riskcategory'),
        ),
    ]
