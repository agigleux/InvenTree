# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-22 11:53
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('part', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch', models.CharField(blank=True, help_text='Batch code for this build output', max_length=100, null=True)),
                ('status', models.PositiveIntegerField(choices=[(40, 'Complete'), (10, 'Pending'), (20, 'Holding'), (30, 'Cancelled')], default=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('creation_date', models.DateField(auto_now=True)),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('title', models.CharField(help_text='Brief description of the build', max_length=100)),
                ('quantity', models.PositiveIntegerField(default=1, help_text='Number of parts to build', validators=[django.core.validators.MinValueValidator(1)])),
                ('notes', models.TextField(blank=True)),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='builds', to='part.Part')),
            ],
        ),
    ]
