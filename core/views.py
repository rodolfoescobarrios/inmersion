from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import UpdateView
from django.http import HttpResponseForbidden

from .models import (
    Usuario,
    Room,
)

from .forms import (
    CustomUserCreationForm,
    FullInstitucionForm,
    LoginForm,
    UsuarioUpdateForm,
    BuscarUsuarioForm,
)
from .models import Usuario, Direccion

# Decorators to enforce role-based access
def role_required(role_id):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.rol != role_id:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator

paciente_required = role_required(1)
terapeuta_required = role_required(2)
admin_required = role_required(3)
cliente_required = role_required(4)

#--------------------------------------------------Vistas generales-------------------------------------
def home(request):
    return render(request, 'core/home.html')

@login_required
def exit(request):
    logout(request)
    return redirect("home")

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioUpdateForm
    template_name = 'registration/editarUsuario.html'
    success_url = reverse_lazy('home')

#---------------------------------Vistas específicas para el administrador---------------------------------
@login_required
@admin_required
def products(request):
    return render(request, 'core/products.html')

@login_required
@admin_required
def register(request):
    data = {'form': CustomUserCreationForm()}

    if request.method == "POST":
        user_creation_form = CustomUserCreationForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(
                username=user_creation_form.cleaned_data['rut'],
                password=user_creation_form.cleaned_data['password1']
            )
            login(request, user)
            return redirect("home")

    return render(request, 'registration/register.html', data)


@login_required
@admin_required
def institucion(request):
    if request.method == 'POST':
        full_form = FullInstitucionForm(request.POST)
        
        if full_form.is_valid():
            comuna = full_form.cleaned_data['comuna']
            direccion_texto = full_form.cleaned_data['direccion']
            
            direccion, created = Direccion.objects.get_or_create(
                nombre_direccion=direccion_texto,
                comuna=comuna
            )
            
            institucion = full_form.save(commit=False)
            institucion.direccion = direccion
            institucion.save()
            
            return redirect("institucion")
    else:
        full_form = FullInstitucionForm()
    
    return render(request, 'registration/institucion.html', {'form': full_form})
#----------------------------------------------------------------------------------------------------------------------

#------------------------------------Vistas compartidas entre administrador y cliente----------------------------------
@login_required
def buscarUsuario(request):
    if request.user.rol not in [3, 4]:  # 3: Admin, 4: Cliente
        return redirect('error_page')  # Redirige si no es admin ni cliente

    form = BuscarUsuarioForm(request.POST or None)
    
    if form.is_valid():
        rut = form.cleaned_data['rut']
        usuario = Usuario.objects.filter(rut=rut).first()
        
        if usuario:
            return redirect('editarUsuario', pk=usuario.pk)
        else:
            form.add_error('rut', 'Usuario no encontrado.')
    
    return render(request, 'core/buscadorUsuario.html', {'form': form})
#----------------------------------------------------------------------------------------------------------------------

#---------------------------------------Vistas específicas para terapeutas---------------------------------------------
@login_required
@terapeuta_required
def listarPacientes(request):
    terapeuta = request.user
    if not isinstance(terapeuta, Usuario) or terapeuta.rol != 2:  # Verificar si es terapeuta
        return redirect('error_page')  # Redirigir a una página de error o inicio

    # Obtener la institución del terapeuta
    institucion_id = terapeuta.institucion.id

    # Filtrar pacientes de la misma institución
    pacientes = Usuario.objects.filter(institucion_id=institucion_id, rol=1)  # Asumiendo 1 es el rol de Paciente

    return render(request, 'terapeuta/listarPacientes.html', {'pacientes': pacientes})

def chatPaciente(request, paciente_id):
    paciente = get_object_or_404(Usuario, id=paciente_id, rol=1)  # rol=1 para "Paciente"
    
    # Intenta recuperar la sala, si no existe, créala
    sala, created = Room.objects.get_or_create(terapeuta=request.user, paciente=paciente)

    context = {
        'sala': sala,
        'paciente': paciente,
        'room_id': sala.id,  # Pasamos la ID de la sala creada o encontrada
    }
    return render(request, "terapeuta/chatPaciente.html", context)
#----------------------------------------------------------------------------------------------------------------------

#------------------------------------------Vistas específicas para pacientes-------------------------------------------
@login_required
@paciente_required
def miChat(request):
    sala = Room.objects.filter(paciente=request.user).first()  # Filtrar la sala del paciente actual
    return render(request, "paciente/miChat.html", {'sala': sala})
#----------------------------------------------------------------------------------------------------------------------



