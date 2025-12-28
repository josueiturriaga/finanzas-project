from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from finanzas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- [SOLUCIÓN] TUS RUTAS PERSONALIZADAS ---
    # Estas líneas obligan a Django a usar TUS archivos HTML que están junto al login.
    # Es VITAL que vayan ANTES del include de abajo.
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    # (Opcional) Esta es para cuando pinchan el link del correo para poner la nueva clave
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # --- RUTAS DE AUTENTICACIÓN ESTÁNDAR ---
    # Esto habilita la lógica interna (enviar correos, tokens, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # 1. MENÚ Y HOME
    path('', views.menu, name='menu'), 
    path('resumen/', views.home, name='home'),
    
    # 2. BÓVEDA Y OPERACIONES
    path('ahorro/', views.ahorro, name='ahorro'),
    path('transferir/', views.transferir, name='transferir'),
    path('retirar/', views.retirar, name='retirar'),
    path('saldos/', views.saldos, name='saldos'),
    
    # RUTAS DE AJUSTE
    path('actualizar_inversion/', views.actualizar_inversion, name='actualizar_inversion'),
    path('actualizar_ahorro/', views.actualizar_ahorro, name='actualizar_ahorro'),
    
    # --- RUTA PARA EDITAR LA META ---
    path('editar_meta/', views.editar_meta, name='editar_meta'),

    # 3. TRANSACCIONES CRUD
    path('agregar/', views.agregar_transaccion, name='agregar_transaccion'),
    path('editar/<int:id>/', views.editar_transaccion, name='editar_transaccion'),
    path('eliminar/<int:id>/', views.eliminar_transaccion, name='eliminar_transaccion'),
    
    # 4. USUARIO
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registro/', views.registro, name='registro'),
]