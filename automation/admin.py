
from django.contrib import admin
from .models import Device, DeviceReport

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_id','name','desired_ch1','desired_ch2','desired_ch3','desired_ch4','last_seen')
    search_fields = ('device_id','name')

@admin.register(DeviceReport)
class DeviceReportAdmin(admin.ModelAdmin):
    list_display = ('device','ch1','ch2','ch3','ch4','created_at')
    list_filter = ('device',)
