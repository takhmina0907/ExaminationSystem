# Generated by Django 2.2 on 2019-05-01 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0002_auto_20190501_0125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_table',
            name='country',
            field=models.ForeignKey(blank=True, on_delete='CASCADE', to='things.Country'),
        ),
    ]
