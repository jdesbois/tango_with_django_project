# Generated by Django 2.2.6 on 2020-01-27 19:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rango', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.RenameField(
            model_name='page',
            old_name='catergory',
            new_name='category',
        ),
    ]
