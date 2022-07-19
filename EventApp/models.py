from django.db import models

# Create your models here.

class clsUser(models.Model):
    pk_user_id = models.BigAutoField(primary_key=True)
    vhr_user_name = models.CharField(max_length=30,blank=True)
    vhr_email = models.CharField(max_length=30,blank=True)
    vhr_password = models.CharField(max_length=8,blank=True)
    int_if_admin =  models.IntegerField()
    dat_created_datetime = models.DateTimeField()
    int_last_action = models.IntegerField()
    
    def __str__(self) -> str:
        return self.vhr_user_name


class clsEventDetails(models.Model):
    pk_event_id = models.BigAutoField(primary_key=True)
    fk_user = models.ForeignKey("clsUser", on_delete=models.CASCADE,related_name="clsEventDetails_clsUser_1")
    dat_event_start_date_time = models.DateTimeField()
    dat_event_end_date_time = models.DateTimeField()
    vhr_event_name = models.CharField(max_length=30,blank=True)
    vhr_event_venue = models.CharField(max_length=30,blank=True)
    vhr_event_description = models.TextField(max_length=100,blank=True)
    vhr_event_file_upload = models.CharField(max_length=100,blank=True)
    dat_created_datetime = models.DateTimeField()
    int_event_location_type = models.IntegerField(default=1)
    int_if_paid = models.IntegerField(default=0)
    int_last_action = models.IntegerField(default=1)
    
    def __str__(self) -> str:
        return self.vhr_event_name
    pass    