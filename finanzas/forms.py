from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaccion

# --- 1. FORMULARIO DE REGISTRO ---
class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Usuario',
            'class': 'form-input',
            'autocomplete': 'off'
        })
        
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Contraseña',
            'class': 'form-input'
        })
        self.fields['password1'].help_text = "Mínimo 8 caracteres. No uses datos personales obvios."
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirmar contraseña',
            'class': 'form-input'
        })


# --- 2. FORMULARIO DE TRANSACCIONES (Corregido) ---
class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        # AQUÍ AGREGUÉ 'cuenta' PARA QUE APAREZCA EL SELECTOR DE BANCOS
        fields = ['titulo', 'monto', 'tipo', 'categoria', 'metodo_pago', 'cuenta', 'tipo_gasto', 'fecha']
        
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), 
            'titulo': forms.TextInput(attrs={'placeholder': 'Ej: Supermercado Lider', 'class': 'form-control'}),
            # Opcional: puedes agregar clases a 'cuenta' si quieres estilos específicos, 
            # pero por ahora funcionará bien así.
        }