# Generated by Django 2.2.5 on 2019-10-26 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_auto_20191022_1218'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='membership',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='membership',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Забанен ли?'),
        ),
    ]
