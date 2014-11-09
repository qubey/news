# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WordCount',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('location', models.CharField(max_length=30)),
                ('word', models.CharField(max_length=128)),
                ('total_count', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
