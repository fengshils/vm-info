# Generated by Django 2.2.2 on 2019-06-14 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_vms_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vms',
            name='uuid',
            field=models.CharField(blank=True, db_index=True, max_length=32, null=True, verbose_name='VM-uuid'),
        ),
    ]
