# Generated by Django 2.0.6 on 2018-11-24 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='hospital',
            options={'ordering': ['state']},
        ),
        migrations.AlterField(
            model_name='hospital',
            name='about',
            field=models.TextField(blank=True, max_length=20480, null=True),
        ),
    ]
