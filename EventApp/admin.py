from django.contrib import admin
# Register your models here.
from .models import clsUser,clsEventDetails

admin.site.register(clsUser)
admin.site.register(clsEventDetails)

