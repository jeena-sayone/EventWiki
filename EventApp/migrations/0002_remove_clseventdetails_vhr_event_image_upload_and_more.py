# Generated by Django 4.0.6 on 2022-07-14 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EventApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clseventdetails',
            name='vhr_event_image_upload',
        ),
        migrations.AddField(
            model_name='clseventdetails',
            name='int_event_location_type',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='clseventdetails',
            name='int_if_paid',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='clseventdetails',
            name='vhr_event_file_upload',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='clseventdetails',
            name='int_last_action',
            field=models.IntegerField(default=1),
        ),
    ]
