# Generated by Django 4.0.6 on 2022-07-14 06:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EventApp', '0003_alter_clseventdetails_fk_user_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clseventdetails',
            old_name='fk_user_id',
            new_name='fk_user',
        ),
    ]
