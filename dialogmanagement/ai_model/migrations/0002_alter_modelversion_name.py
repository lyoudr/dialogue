# Generated by Django 5.0.13 on 2025-03-15 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_model', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelversion',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
