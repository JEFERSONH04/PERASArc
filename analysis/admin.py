from django.contrib import admin

# Register your models here.
from django.urls import path
from django.contrib import admin
from .models import MLModel, HyperparameterDefinition, AnalysisResult, MapeoResultado, UserAnalysis
from django.http import HttpResponse
from .reportes import SimpleReportGenerator

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

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    change_list_template = "admin/analysis/analysisresult/change_list.html"

    def get_urls(self):
        """
        Añade una URL admin propia para generar el reporte.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                'reporte-rapido/',
                self.admin_site.admin_view(self.reporte_rapido),
                name='analysisresult_reporte_rapido'
            ),
        ]
        return custom_urls + urls

    def reporte_rapido(self, request):
        """
        Vista que genera el PDF usando SimpleReportGenerator
        y lo devuelve como adjunto.
        """
        # Opcional: podrías filtrar self.get_queryset(request) si quieres modelo específico
        gen = SimpleReportGenerator()
        pdf = gen.generate_pdf()
        filename = gen.filename()
        response = HttpResponse(
            pdf,
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

@admin.register(MapeoResultado)
class MapeoResultadoAdmin(admin.ModelAdmin):
    list_display = ['model', 'valor_prediccion', 'etiqueta_texto']
    list_filter = ['model']
    search_fields = ['etiqueta_texto']

@admin.register(UserAnalysis)
class UserAnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'user']
    list_filter = ['user']






