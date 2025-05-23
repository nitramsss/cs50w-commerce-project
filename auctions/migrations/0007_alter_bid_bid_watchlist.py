# Generated by Django 5.1.4 on 2024-12-12 23:43

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_comment_date_commented'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='bid',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.CreateModel(
            name='Watchlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ManyToManyField(blank=True, related_name='favorites', to='auctions.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
