from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import MLModel, HyperparameterDefinition

class HyperparameterInline(admin.TabularInline):
    model = HyperparameterDefinition
    extra = 0
    fields = ('position', 'key_hint', 'dtype', 'required', 'help_text')
    ordering = ('position',)

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display    = ('name', 'version', 'framework', 'owner', 'created_at')
    list_filter     = ('framework', 'created_at', 'owner')
    search_fields   = ('name', 'version')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'version', 'framework', 'file')
        }),
        ('Ownership & Audit', {
            'fields': ('owner', 'created_at'),
        }),
    )
    inlines = [HyperparameterInline]
    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)







