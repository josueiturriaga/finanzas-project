from django.db import models
from django.contrib.auth.models import User

# MODELO PARA TU META PERSONALIZADA
class MetaAhorro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50, default="Mi Meta")
    monto_objetivo = models.IntegerField(default=1000000)

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso 🤑'),
        ('gasto', 'Gasto 💸'),
    ]

    CATEGORIA_CHOICES = [
        # --- INGRESOS ---
        ('sueldo', 'Sueldo'),
        ('negocio', 'Negocio'),
        ('mesada_tatas', 'Mesada Tatas'),
        ('mesada_luis', 'Mesada Tío Luis'),
        
        # Categorías Bóveda
        ('retorno_ahorro', 'Retiro de Ahorros 🐖'), 
        ('perdida_ahorro', 'Pérdida Ahorro (Ajuste) 📉'), # <--- [NUEVO]
        
        ('retorno_inversion', 'Retiro de Inversión 📈'),
        ('perdida_inversion', 'Pérdida de Mercado 📉'),
        
        ('otro_ingreso', 'Otro Ingreso'),

        # --- GASTOS ---
        ('bencina', 'Bencina'),
        ('diezmo', 'Diezmo'),
        ('pasajes', 'Pasajes'),
        ('regalos', 'Regalos / Novia'),
        ('comida', 'Comida / Supermercado'),
        
        ('inversion', 'Inversión 📈'),
        ('ganancia_inversion', 'Ganancia de Mercado 📈'),
        
        ('ahorro', 'Ahorro 🐖'),
        ('ganancia_ahorro', 'Ganancia Ahorro (Interés/Hallazgo) 🐖'), # <--- [NUEVO]
        
        ('arriendo', 'Arriendo / Casa'),
        ('servicios', 'Cuentas (Luz/Agua)'),
        ('salud', 'Salud / Farmacia'),
        ('ocio', 'Ocio / Salidas'),
        ('varios', 'Varios / Otros'),
    ]

    METODO_PAGO_CHOICES = [
        ('debito', 'Tarjeta Débito'),
        ('credito', 'Tarjeta Crédito'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('ajuste', 'Ajuste Automático'),
    ]

    TIPO_GASTO_CHOICES = [
        ('fijo', 'Gasto Fijo (Obligatorio)'),
        ('variable', 'Gasto Variable (Necesario)'),
        ('hormiga', 'Gasto Hormiga (Evitable)'),
        ('inversion', 'Inversión / Ahorro'),
        ('na', 'No Aplica (Ingresos)'),
    ]

    CUENTAS_CHOICES = [
        ('efectivo', 'Efectivo (Billetera)'),
        ('banco_estado', 'Banco Estado'),
        ('banco_falabella', 'Banco Falabella'),
        ('santander', 'Santander'),
        ('mach', 'MACH'),
        ('Inversiones', 'Bóveda Inversiones'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100, verbose_name="Concepto")
    monto = models.IntegerField(verbose_name="Monto (CLP)")
    fecha = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='gasto')
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='varios')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='debito')
    cuenta = models.CharField(max_length=50, choices=CUENTAS_CHOICES, default='efectivo')
    tipo_gasto = models.CharField(max_length=20, choices=TIPO_GASTO_CHOICES, default='variable')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} (${self.monto})"