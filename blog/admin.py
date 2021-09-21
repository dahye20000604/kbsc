from django.contrib import admin

from .models import LithiumBattery, Member

class LithiumBatteryAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_period','charging_start_time','charging_finish_time','now_time')

admin.site.register(LithiumBattery, LithiumBatteryAdmin)
admin.site.register(Member)