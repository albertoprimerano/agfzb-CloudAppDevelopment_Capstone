from django.contrib import admin
from .models import CarMake, CarModel


# Car Model Inline
class CarModelInline(admin.ModelAdmin):
    model = CarModel
    extra = 5


# Car Make Inline
class CarMakeInline(admin.ModelAdmin):
    model = CarMake
    extra = 5


# Car Make Admin
class CarMakeAdmin(admin.ModelAdmin):
    model = CarMake
    inlines = [CarModelInline]


# Car Model Admin
class CarModelAdmin(admin.ModelAdmin):
    model = CarModel
    inlines = [CarMakeInline]


admin.site.register(CarMake)
admin.site.register(CarModel)
