from django.contrib import admin
from .models import Transaccion

# Esta clase configura cómo se ve la tabla en el panel de admin
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'titulo', 'monto', 'tipo', 'categoria', 'tipo_gasto') # Columnas visibles
    list_filter = ('tipo', 'categoria', 'metodo_pago', 'tipo_gasto') # Filtros a la derecha
    search_fields = ('titulo',) # Barra de búsqueda
    ordering = ('-fecha',) # Ordenar por fecha descendente

admin.site.register(Transaccion, TransaccionAdmin)