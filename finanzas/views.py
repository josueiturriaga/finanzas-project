from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages
import json
import datetime

# IMPORTAMOS TUS MODELOS Y FORMULARIOS
from .models import Transaccion, MetaAhorro
from .forms import TransaccionForm, RegistroForm 

# --- VISTA MENÚ PRINCIPAL ---
@login_required
def menu(request):
    return render(request, 'menu.html')

# --- VISTA HOME (RESUMEN) ---
@login_required
def home(request):
    transacciones = Transaccion.objects.filter(usuario=request.user)

    # --- CORRECCIÓN DE FILTROS ---
    hoy = datetime.date.today()
    
    # Intentamos obtener los datos del filtro (URL)
    mes_filtrado = request.GET.get('mes')
    anio_filtrado = request.GET.get('anio')

    # Si existen los datos en la URL, los usamos. Si no, usamos el mes actual.
    if mes_filtrado and anio_filtrado:
        mes_filtrado = int(mes_filtrado)
        anio_filtrado = int(anio_filtrado)
    else:
        mes_filtrado = hoy.month
        anio_filtrado = hoy.year

    # Aplicamos el filtro SIEMPRE. Así, por defecto, solo ves el mes actual.
    transacciones = transacciones.filter(fecha__month=mes_filtrado, fecha__year=anio_filtrado)
    
    transacciones = transacciones.order_by('-fecha')

    # SALDO DISPONIBLE (Ignora ajustes de inversión y ahorro para no afectar efectivo real)
    txs_liquidas = transacciones.exclude(categoria__in=['ganancia_inversion', 'perdida_inversion', 'ganancia_ahorro', 'perdida_ahorro'])
    total_ingresos = txs_liquidas.filter(tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
    total_gastos = txs_liquidas.filter(tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_actual = total_ingresos - total_gastos

    # Gráficos
    nombres = dict(Transaccion.CATEGORIA_CHOICES)
    gastos_cat = transacciones.filter(tipo='gasto').exclude(categoria__in=['ganancia_inversion', 'ganancia_ahorro']).values('categoria').annotate(total=Sum('monto'))
    labels_gastos = [nombres.get(item['categoria'], item['categoria']) for item in gastos_cat]
    data_gastos = [int(item['total']) for item in gastos_cat]

    ingresos_cat = transacciones.filter(tipo='ingreso').exclude(categoria__in=['perdida_inversion', 'perdida_ahorro']).values('categoria').annotate(total=Sum('monto'))
    labels_ingresos = [nombres.get(item['categoria'], item['categoria']) for item in ingresos_cat]
    data_ingresos = [int(item['total']) for item in ingresos_cat]

    fechas_bd = Transaccion.objects.dates('fecha', 'year')
    anios_con_datos = set([fecha.year for fecha in fechas_bd])
    anios_futuros = set(range(2025, 2036))
    lista_final = sorted(list(anios_con_datos | anios_futuros), reverse=True)

    return render(request, 'home.html', {
        'transacciones': transacciones,
        'saldo': saldo_actual,
        'ingresos': total_ingresos,
        'gastos': total_gastos,
        'labels_gastos': json.dumps(labels_gastos),
        'data_gastos': json.dumps(data_gastos),
        'labels_ingresos': json.dumps(labels_ingresos),
        'data_ingresos': json.dumps(data_ingresos),
        'lista_anios': lista_final,
        'mes_actual': mes_filtrado,
        'anio_actual': anio_filtrado,
    })

# --- VISTA AHORRO E INVERSIÓN (MODIFICADA) ---
@login_required
def ahorro(request):
    txs = Transaccion.objects.filter(usuario=request.user)

    # 1. AHORRO (Ahora incluye ajustes)
    entradas_aho = txs.filter(tipo='gasto', categoria__in=['ahorro', 'ganancia_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
    salidas_aho = txs.filter(tipo='ingreso', categoria__in=['retorno_ahorro', 'perdida_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_ahorro = entradas_aho - salidas_aho

    # 2. INVERSIÓN
    entradas_inv = txs.filter(tipo='gasto', categoria__in=['inversion', 'ganancia_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
    salidas_inv = txs.filter(tipo='ingreso', categoria__in=['retorno_inversion', 'perdida_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_inversion = entradas_inv - salidas_inv
    
    # 3. RETIRADO REAL (Solo retiros manuales a billetera, ignora pérdidas)
    retiros_ahorro_real = txs.filter(tipo='ingreso', categoria='retorno_ahorro').aggregate(Sum('monto'))['monto__sum'] or 0
    retiros_reales_inv = txs.filter(tipo='ingreso', categoria='retorno_inversion').aggregate(Sum('monto'))['monto__sum'] or 0
    
    total_retirado = retiros_ahorro_real + retiros_reales_inv
    saldo_boveda = saldo_ahorro + saldo_inversion

    # --- 4. META PERSONALIZADA ---
    mi_meta, created = MetaAhorro.objects.get_or_create(
        usuario=request.user,
        defaults={'nombre': 'Mi Primer Auto', 'monto_objetivo': 5000000}
    )

    progreso_monto = saldo_ahorro 
    if mi_meta.monto_objetivo > 0:
        porcentaje = (progreso_monto / mi_meta.monto_objetivo) * 100
    else:
        porcentaje = 0
    
    if porcentaje > 100: porcentaje = 100

    labels_boveda = ['Ahorro Puro', 'Inversiones', 'Retiros Reales']
    data_boveda = [saldo_ahorro, saldo_inversion, total_retirado]

    return render(request, 'ahorro.html', {
        'saldo_boveda': saldo_boveda,
        'total_ahorrado': saldo_ahorro,
        'total_invertido': saldo_inversion,
        'total_retirado': total_retirado,
        'mi_meta': mi_meta,
        'porcentaje_auto': int(porcentaje),
        'labels_boveda': json.dumps(labels_boveda),
        'data_boveda': json.dumps(data_boveda),
    })

# --- NUEVA: ACTUALIZAR AHORRO ---
@login_required
def actualizar_ahorro(request):
    if request.method == 'POST':
        monto_real = int(request.POST.get('monto_real'))
        
        txs = Transaccion.objects.filter(usuario=request.user)
        # Calculamos saldo actual considerando ajustes previos
        entradas = txs.filter(tipo='gasto', categoria__in=['ahorro', 'ganancia_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
        salidas = txs.filter(tipo='ingreso', categoria__in=['retorno_ahorro', 'perdida_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
        saldo_sistema = entradas - salidas
        
        diferencia = monto_real - saldo_sistema

        if diferencia > 0:
            Transaccion.objects.create(
                usuario=request.user, monto=diferencia, titulo='Ajuste Ahorro (+)', tipo='gasto', 
                categoria='ganancia_ahorro', fecha=datetime.date.today(), metodo_pago='ajuste', cuenta='efectivo', tipo_gasto='inversion'
            )
            messages.success(request, f'¡Ahorro ajustado! +${diferencia} 🐖')
        elif diferencia < 0:
            perdida = abs(diferencia)
            Transaccion.objects.create(
                usuario=request.user, monto=perdida, titulo='Ajuste Ahorro (-)', tipo='ingreso', 
                categoria='perdida_ahorro', fecha=datetime.date.today(), metodo_pago='ajuste', cuenta='efectivo', tipo_gasto='na'
            )
            messages.warning(request, f'Ahorro ajustado. -${perdida} 📉')
        return redirect('ahorro')
    return redirect('ahorro')

# --- ACTUALIZAR INVERSIÓN ---
@login_required
def actualizar_inversion(request):
    if request.method == 'POST':
        monto_real = int(request.POST.get('monto_real')) 
        
        txs = Transaccion.objects.filter(usuario=request.user)
        entradas = txs.filter(tipo='gasto', categoria__in=['inversion', 'ganancia_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
        salidas = txs.filter(tipo='ingreso', categoria__in=['retorno_inversion', 'perdida_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
        saldo_sistema = entradas - salidas
        
        diferencia = monto_real - saldo_sistema

        if diferencia > 0:
            Transaccion.objects.create(
                usuario=request.user, monto=diferencia, titulo='Rentabilidad Inversión', tipo='gasto', 
                categoria='ganancia_inversion', fecha=datetime.date.today(), metodo_pago='ajuste', cuenta='Inversiones', tipo_gasto='inversion'
            )
            messages.success(request, f'¡Genial! Ganaste ${diferencia} 📈')

        elif diferencia < 0:
            perdida = abs(diferencia)
            Transaccion.objects.create(
                usuario=request.user, monto=perdida, titulo='Pérdida de Valor', tipo='ingreso', 
                categoria='perdida_inversion', fecha=datetime.date.today(), metodo_pago='ajuste', cuenta='Inversiones', tipo_gasto='na'
            )
            messages.warning(request, f'Ajuste realizado. Mercado a la baja: -${perdida} 📉')

        return redirect('ahorro')
    return redirect('ahorro')

# --- VISTAS RESTANTES (Editar Meta, Transferir, Retirar, etc.) ---
@login_required
def editar_meta(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_meta')
        monto = request.POST.get('monto_meta')
        meta = MetaAhorro.objects.get(usuario=request.user)
        meta.nombre = nombre
        meta.monto_objetivo = int(monto)
        meta.save()
        messages.success(request, '¡Meta actualizada correctamente! 🎯')
        return redirect('ahorro')
    return redirect('ahorro')

# --- TRANSFERIR (CON FECHA) ---
@login_required
def transferir(request):
    if request.method == 'POST':
        monto = int(request.POST.get('monto'))
        destino = request.POST.get('destino')
        concepto = request.POST.get('concepto')
        origen_cuenta = request.POST.get('origen_cuenta')
        fecha_usuario = request.POST.get('fecha') # Capturamos la fecha

        txs = Transaccion.objects.filter(usuario=request.user)
        ingresos_cuenta = txs.filter(cuenta=origen_cuenta, tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
        gastos_cuenta = txs.filter(cuenta=origen_cuenta, tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
        saldo_en_origen = ingresos_cuenta - gastos_cuenta

        if monto > saldo_en_origen:
            return render(request, 'transferir.html', {'error': f'¡Fondos insuficientes!'})

        # Creamos la transacción usando la fecha seleccionada por el usuario
        Transaccion.objects.create(
            usuario=request.user, 
            monto=monto, 
            titulo=concepto, 
            tipo='gasto', 
            categoria=destino, 
            fecha=fecha_usuario, # Usamos la fecha del calendario
            metodo_pago='transferencia', 
            cuenta=origen_cuenta, 
            tipo_gasto='inversion'
        )
        return redirect('ahorro')
    return render(request, 'transferir.html')

@login_required
def retirar(request):
    if request.method == 'POST':
        monto = int(request.POST.get('monto'))
        origen = request.POST.get('origen') 
        destino_cuenta = request.POST.get('destino_cuenta')

        txs = Transaccion.objects.filter(usuario=request.user)
        
        # Calculamos saldo DISPONIBLE (incluyendo ganancias)
        if origen == 'inversion':
             entradas = txs.filter(tipo='gasto', categoria__in=['inversion', 'ganancia_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
             salidas = txs.filter(tipo='ingreso', categoria__in=['retorno_inversion', 'perdida_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
             saldo_en_caja = entradas - salidas
             cat_retiro = 'retorno_inversion'
        else:
             # Ahorro ahora también incluye ganancias
             entradas = txs.filter(tipo='gasto', categoria__in=['ahorro', 'ganancia_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
             salidas = txs.filter(tipo='ingreso', categoria__in=['retorno_ahorro', 'perdida_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
             saldo_en_caja = entradas - salidas
             cat_retiro = 'retorno_ahorro'

        if monto > saldo_en_caja:
            return render(request, 'retirar.html', {'error': f'Error: Solo tienes ${saldo_en_caja} disponibles.'})

        Transaccion.objects.create(
            usuario=request.user, monto=monto, titulo=f"Retiro desde {origen}", tipo='ingreso',
            categoria=cat_retiro, fecha=datetime.date.today(), metodo_pago='transferencia', cuenta=destino_cuenta, tipo_gasto='na'
        )
        return redirect('ahorro')
    return render(request, 'retirar.html')

@login_required
def agregar_transaccion(request):
    initial_data = {'tipo': request.GET.get('tipo'), 'categoria': request.GET.get('categoria'), 'fecha': datetime.date.today()}
    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.usuario = request.user
            tx.save()
            return redirect('menu') 
    else: form = TransaccionForm(initial=initial_data)
    return render(request, 'agregar.html', {'form': form})

@login_required
def editar_transaccion(request, id):
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    if request.method == 'POST':
        form = TransaccionForm(request.POST, instance=transaccion)
        if form.is_valid(): form.save(); return redirect('home')
    else: form = TransaccionForm(instance=transaccion)
    return render(request, 'agregar.html', {'form': form})

@login_required
def eliminar_transaccion(request, id):
    transaccion = get_object_or_404(Transaccion, id=id, usuario=request.user)
    transaccion.delete()
    return redirect('home')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save(); messages.success(request, f'¡Cuenta creada!'); return redirect('login')
    else: form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

@login_required
def saldos(request):
    txs = Transaccion.objects.filter(usuario=request.user)
    labels, data, lista_saldos = [], [], []

    cuentas_usadas = txs.exclude(cuenta='Inversiones').values_list('cuenta', flat=True).distinct()
    for c in cuentas_usadas:
        ingresos = txs.filter(cuenta=c, tipo='ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
        gastos = txs.filter(cuenta=c, tipo='gasto').aggregate(Sum('monto'))['monto__sum'] or 0
        saldo = ingresos - gastos
        if saldo > 0:
            nombre = c.replace('_', ' ').title()
            labels.append(nombre); data.append(saldo); lista_saldos.append({'nombre': nombre, 'monto': saldo})

    # AHORRO (Cálculo corregido)
    ent_aho = txs.filter(tipo='gasto', categoria__in=['ahorro', 'ganancia_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
    sal_aho = txs.filter(tipo='ingreso', categoria__in=['retorno_ahorro', 'perdida_ahorro']).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_ahorro = ent_aho - sal_aho
    if saldo_ahorro > 0:
        labels.append("Ahorro"); data.append(saldo_ahorro); lista_saldos.append({'nombre': "Ahorro (Bóveda)", 'monto': saldo_ahorro})

    # INVERSION (Cálculo corregido)
    ent_inv = txs.filter(tipo='gasto', categoria__in=['inversion', 'ganancia_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
    sal_inv = txs.filter(tipo='ingreso', categoria__in=['retorno_inversion', 'perdida_inversion']).aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_inv = ent_inv - sal_inv
    if saldo_inv > 0:
        labels.append("Inversión"); data.append(saldo_inv); lista_saldos.append({'nombre': "Inversión (Bóveda)", 'monto': saldo_inv})

    return render(request, 'saldos.html', {
        'labels': json.dumps(labels), 'data': json.dumps(data), 'lista_saldos': lista_saldos, 'total_capital': sum(data)
    })