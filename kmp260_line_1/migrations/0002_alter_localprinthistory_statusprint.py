# Generated by Django 4.2 on 2024-01-16 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmp260_line_1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localprinthistory',
            name='StatusPrint',
            field=models.BooleanField(),
        ),
    ]
