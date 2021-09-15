from django import forms
from django.core.exceptions import ValidationError

class LithiumBattery(forms.form):
    name=models.CharField(max_length=10)
    kind=models.CharField(max_length=20)
    battery_capacity=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    rated_input_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_voltage=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    charger_current=models.DecimalField(default=0, decimal_places=2, max_digits=20)
    purchase_period=models.DateField(editable=True, auto_now_add=True)

    charging_start_time=models.DateTimeField(editable=True, auto_now_add=True)

    loss=models.DecimalField(default=1.2, decimal_places=2, max_digits=20)
    min_voltage=models.DecimalField(default=3.7, decimal_places=2, max_digits=20)
    max_voltage=models.DecimalField(default=4.2, decimal_places=2, max_digits=20)

    def add(self):
        data=self.cleaned_data
        
        if charger_current<rated_input_current:
            raise ValidationError(_('화재발생의 위험이 있습니다'))
        
