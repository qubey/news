# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trends', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSources',
            fields=[
                ('location', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('doc_count', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='wordcount',
            name='avg_doc_freq',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
