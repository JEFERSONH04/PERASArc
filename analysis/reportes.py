# analysis/reports_usage.py

import io, json
import datetime
from django.utils import timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models import Count, Avg, Min, Max, F, DurationField, ExpressionWrapper
from .models import AnalysisResult

class SimpleReportGenerator:
    def __init__(self, queryset=None):
        self.qs = queryset or AnalysisResult.objects.filter(status__in=['SUCCESS','FAILURE'])

    def _time_expr(self):
        return ExpressionWrapper(
            F('completed_at') - F('created_at'),
            output_field=DurationField()
        )

    def _model_stats(self):
        """
        Retorna una lista de dicts con:
          - model__name
          - model__version
          - usage (int)
          - avg_time, min_time, max_time en segundos (float)
        """
        expr = self._time_expr()
        qs = self.qs.values(
            'model__name', 'model__version'
        ).annotate(
            count=Count('id'),
            avg_time=Avg(expr),
            min_time=Min(expr),
            max_time=Max(expr),
        ).order_by('-count')

        stats = []
        for row in qs:
            # Para cada campo temporal, normalizar a segundos
            for key in ('avg_time', 'min_time', 'max_time'):
                val = row.get(key)
                if isinstance(val, datetime.timedelta):
                    seconds = val.total_seconds()
                elif val is None:
                    seconds = 0.0
                else:
                    # asumo que ya viene en segundos
                    seconds = float(val)
                row[key] = round(seconds, 2)
            stats.append(row)
        return stats

    def _user_stats(self):
        qs = self.qs.values('dataset__owner__username').annotate(
            count=Count('id')
        ).order_by('-count')
        return [{'user': r['dataset__owner__username'], 'count': r['count']} for r in qs]
    

    def _model_user_stats(self):
        """
        Retorna una lista de dicts con:
          - label: "Modelo vVersión"
          - count: número de usuarios distintos que lo usaron
        """
        qs = (
            self.qs
            .values('model__name', 'model__version')
            # contamos usuarios únicos por modelo-version
            .annotate(user_count=Count('dataset__owner__username', distinct=True))
            .order_by('-user_count')
        )
        return [
            {
                'label': f"{r['model__name']} v{r['model__version']}",
                'count': r['user_count']
            }
            for r in qs
        ]
    
    def _status_stats(self):
        """
        Retorna lista de dicts:
          {
            'model__name','model__version',
            'success_count','failure_count'
          }
        """
        qs = (
            self.qs
            .values('model__name','model__version')
            .annotate(
                success_count=Count('id', filter=Q(status='SUCCESS')),
                failure_count=Count('id', filter=Q(status='FAILURE'))
            )
            .order_by('-success_count')
        )
        return [
            {
                'model__name': r['model__name'],
                'model__version': r['model__version'],
                'success_count': r['success_count'],
                'failure_count': r['failure_count']
            }
            for r in qs
        ]

    def _build_model_usage_chart(self, model_stats):
        labels = [f"{r['model__name']} v{r['model__version']}" for r in model_stats]
        counts = [r['count'] for r in model_stats]
        fig, ax = plt.subplots(figsize=(6,3))
        ax.bar(labels, counts, color='skyblue')
        ax.set_title('Ejecuciones por Modelo-Version')
        ax.set_ylabel('Cantidad de tareas')
        plt.xticks(rotation=45, ha='right')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='PNG')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def _build_user_pie(self, user_stats):
        labels = [u['user'] for u in user_stats]
        sizes  = [u['count'] for u in user_stats]
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title('Distribución de Tareas por Usuario')
        buf = io.BytesIO()
        fig.savefig(buf, format='PNG', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def _build_status_chart(self, status_stats):
        labels    = [f"{r['model__name']} v{r['model__version']}" for r in status_stats]
        success   = [r['success_count'] for r in status_stats]
        failure   = [r['failure_count'] for r in status_stats]
        fig, ax = plt.subplots(figsize=(6,3))
        ax.bar(labels, success,  color='green', label='Éxito')
        ax.bar(labels, failure, bottom=success, color='red', label='Fallido')
        ax.set_title('Éxito vs Fallo por Modelo-Version')
        ax.set_ylabel('Cantidad de tareas')
        plt.xticks(rotation=45, ha='right')
        ax.legend()
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='PNG')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def _user_preferences(self):
        """
        Para cada usuario, determina el modelo+versión más usado y el conteo.
        Retorna lista de dicts:
          [{'user','model','version','count'}, …]
        """
        # 1) Agregamos conteos por usuario y modelo-version
        qs = (
            self.qs
            .values('dataset__owner__username',
                    'model__name',
                    'model__version')
            .annotate(count=Count('id'))
            .order_by('dataset__owner__username', '-count')
        )

        # 2) Por cada usuario, tomamos el primer registro (mayor count)
        prefs = {}
        for r in qs:
            user = r['dataset__owner__username']
            if user not in prefs:
                prefs[user] = {
                    'user': user,
                    'model': r['model__name'],
                    'version': r['model__version'],
                    'count': r['count']
                }
        # 3) Devolvemos como lista
        return list(prefs.values())

    def _build_pref_chart(self, prefs):
        """
        Genera un bar chart donde cada usuario tiene una barra
        del conteo de su modelo preferido.
        """
        labels = [p['user'] for p in prefs]
        counts = [p['count'] for p in prefs]
        fig, ax = plt.subplots(figsize=(6,3))
        ax.bar(labels, counts, color='mediumpurple')
        ax.set_title('Modelo preferido: tareas por usuario')
        ax.set_ylabel('Veces ejecutado')
        plt.xticks(rotation=45, ha='right')
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='PNG')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    def _build_model_user_pie(self, stats):
        """
        Genera un pie chart con etiquetas = modelo+versión
        y tamaños = número de usuarios distintos.
        """
        labels = [r['label'] for r in stats]
        sizes  = [r['count'] for r in stats]
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('Usuarios únicos por Modelo-Version')
        buf = io.BytesIO()
        fig.savefig(buf, format='PNG', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf


    def _hourly_heatmap(self):
        """
        Heatmap con eje Y = hora (0–23) **correcta** en hora Colombia.
        """
        # 1) Localizar todos los created_at a Bogota
        times = [(r.created_at, r.status) for r in self.qs]
        df = pd.DataFrame(times, columns=['created_at','status'])


        # 2) Extraer día y hora
        days_order = [
        'Monday','Tuesday','Wednesday','Thursday',
        'Friday','Saturday','Sunday'
        ]
        df['day']  = pd.Categorical(
            df['created_at'].dt.day_name(),
            categories=days_order,
            ordered=True
        )
        df['hour'] = df['created_at'].dt.hour

        # 3) Pivot: conteo por hora y día
        pivot = df.pivot_table(
            index='hour',
            columns='day',
            aggfunc='size',
            fill_value=0
        )

        # 4) Dibujar heatmap (origin='lower' para hora 0 abajo)
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(pivot, aspect='auto', origin='lower', cmap='Blues')

        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
        ax.set_yticks(range(24))
        ax.set_yticklabels(range(24))
        ax.set_xlabel('Día de la semana')
        ax.set_ylabel('Hora del día (Bogotá)')
        ax.set_title('Tareas por día y hora (Hora Colombia)')

        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Número de tareas')

        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='PNG')
        plt.close(fig)
        buf.seek(0)
        return buf

    def generate_pdf(self):
        buffer = io.BytesIO()
        doc    = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elems  = []

        # 1. Modelos
        elems.append(Paragraph("1. Modelos más usados", styles['Heading2']))
        model_stats = self._model_stats()
        table = [['Modelo','Versión','Ejecuciones','Promedio (s)','Mínimo (s)','Máximo (s)']]
        for m in model_stats:
            table.append([
                m['model__name'], m['model__version'],
                m['count'], m['avg_time'], m['min_time'], m['max_time']
            ])
        elems.append(Table(table, hAlign='LEFT'))
        elems.append(Spacer(1,12))
        elems.append(Image(self._build_model_usage_chart(model_stats), width=450, height=200))
        elems.append(Spacer(1,24))

        # 2. Usuarios
        elems.append(Paragraph("2. Usuarios y su interacción", styles['Heading2']))
        user_stats = self._user_stats()
        table = [['Usuario','Tareas']]
        for u in user_stats:
            table.append([u['user'], u['count']])
        elems.append(Table(table, hAlign='LEFT'))
        elems.append(Spacer(1,12))
        elems.append(Image(self._build_user_pie(user_stats), width=200, height=200))
        elems.append(Spacer(1,24))

        # 3. Éxito vs Fallo
        elems.append(Paragraph("3. Tareas Exitosas vs Fallidas", styles['Heading2']))
        status_stats = self._status_stats()
        table = [['Modelo','Versión','Éxitos','Fallos']]
        for s in status_stats:
            table.append([
                s['model__name'], s['model__version'],
                s['success_count'], s['failure_count']
            ])
        elems.append(Table(table, hAlign='LEFT'))
        elems.append(Spacer(1,12))
        elems.append(Image(self._build_status_chart(status_stats), width=450, height=200))

                # 4. Modelo preferido por los usuarios
        elems.append(Paragraph("4. Modelo preferido por los usuarios", styles['Heading2']))
        prefs = self._user_preferences()

        # 4.1 Tabla de preferencias
        table_data = [['Usuario','Modelo preferido','Versión','Veces usado']]
        for p in prefs:
            table_data.append([p['user'], p['model'], p['version'], p['count']])
        elems.append(Table(table_data, hAlign='LEFT'))
        elems.append(Spacer(1, 12))

        # 4.2 Gráfica de barras
        elems.append(Image(self._build_pref_chart(prefs), width=450, height=200))

                # 5. Usuarios distintos por Modelo-Version
        elems.append(Paragraph(
            "5. Cantidad de usuarios distintos por Modelo-Version",
            styles['Heading2']
        ))
        mu_stats = self._model_user_stats()
        # 5.1 Tabla
        table_data = [['Modelo-Version','Usuarios únicos']]
        for m in mu_stats:
            table_data.append([m['label'], m['count']])
        elems.append(Table(table_data, hAlign='LEFT'))
        elems.append(Spacer(1,12))
        # 5.2 Pie chart
        elems.append(Image(self._build_model_user_pie(mu_stats), width=300, height=300))
        elems.append(Spacer(1,24))

        # Sección 3: Heatmap Horario
        elems.append(Paragraph("4. Heatmap Horario de Ejecución", styles['Heading2']))
        elems.append(Image(self._hourly_heatmap(), width=500, height=300))

        doc.build(elems)
        return buffer.getvalue()

    def _build_bar_chart(self, data):
        labels = [f"{r['model__name']} v{r['model__version']}" for r in data]
        counts = [r['usage'] for r in data]
        fig, ax = plt.subplots(figsize=(6,3))
        ax.bar(labels, counts, color='teal')
        plt.xticks(rotation=45, ha='right')
        ax.set_title("Uso por Modelo y Versión")
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='PNG')
        plt.close(fig)
        buf.seek(0)
        return buf
    
    

    def _build_pie_chart(self, data):
        labels = [u['user'] for u in data]
        counts = [u['count'] for u in data]
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(counts, labels=labels, autopct='%1.1f%%')
        ax.set_title("Distribución de Usuarios")
        buf = io.BytesIO()
        fig.savefig(buf, format='PNG', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    @staticmethod
    def filename():
        hoy = timezone.localdate().strftime("%d-%m-%Y")
        return f"Reporte del {hoy}.pdf"