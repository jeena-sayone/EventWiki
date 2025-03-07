# Generated by Django 4.0.6 on 2022-07-14 06:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('EventApp', '0002_remove_clseventdetails_vhr_event_image_upload_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clseventdetails',
            name='fk_user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clsEventDetails_clsUser_1', to='EventApp.clsuser'),
        ),
        migrations.AlterField(
            model_name='clseventdetails',
            name='pk_event_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='clsuser',
            name='pk_user_id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
