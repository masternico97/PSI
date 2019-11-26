# Generated by Django 2.1.7 on 2019-11-12 18:22

import datamodel.models
import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat1', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('cat2', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('cat3', models.IntegerField(default=4, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('cat4', models.IntegerField(default=6, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('mouse', models.IntegerField(default=59, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(63)])),
                ('cat_turn', models.BooleanField(default=True)),
                ('status', models.IntegerField(default=datamodel.models.GameStatus(1))),
                ('cat_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_as_cat', to=settings.AUTH_USER_MODEL)),
                ('mouse_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_as_mouse', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.IntegerField(default=-1)),
                ('target', models.IntegerField(default=-1)),
                ('date', models.DateField(default=datetime.date.today)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moves', to='datamodel.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
