# Generated by Django 5.1.6 on 2025-04-12 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('textbook', '0008_library'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='library',
            name='textbooks',
        ),
        migrations.AddField(
            model_name='library',
            name='collections',
            field=models.ManyToManyField(blank=True, related_name='libraries', to='textbook.collection'),
        ),
    ]
