# Generated by Django 5.0.6 on 2024-07-08 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_solditems'),
    ]

    operations = [
        migrations.AddField(
            model_name='solditems',
            name='quantity',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
