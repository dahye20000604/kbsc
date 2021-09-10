from django.contrib import admin

from .models import LithiumBattery, Member

class LithiumBatteryAdmin(admin.ModelAdmin):
    readonly_fields = ('purchase_period',)

admin.site.register(LithiumBattery, LithiumBatteryAdmin)
admin.site.register(Member)