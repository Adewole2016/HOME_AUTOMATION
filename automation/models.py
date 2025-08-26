
from django.db import models

class Device(models.Model):
    device_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=128, default='4CH Controller')
    desired_ch1 = models.BooleanField(default=False)
    desired_ch2 = models.BooleanField(default=False)
    desired_ch3 = models.BooleanField(default=False)
    desired_ch4 = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"

class DeviceReport(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='reports')
    ch1 = models.BooleanField(default=False)
    ch2 = models.BooleanField(default=False)
    ch3 = models.BooleanField(default=False)
    ch4 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
