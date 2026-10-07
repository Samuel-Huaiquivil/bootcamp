from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from apps.courses.models import Curso
from apps.orders.services import cupos_disponibles
from apps.users.models import Usuario


class RegistroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.ESTUDIANTE
        if commit:
            usuario.save()
        return usuario


class ProfesorForm(RegistroForm):
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.Rol.PROFESOR
        if commit:
            usuario.save()
        return usuario


class CursoForm(forms.ModelForm):
    profesores = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(rol=Usuario.Rol.PROFESOR),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Curso
        fields = (
            'nombre', 'descripcion', 'objetivos', 'cupos', 'precio',
            'fecha_inicio', 'fecha_termino', 'fecha_limite_inscripcion',
            'estado', 'profesores',
        )
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'objetivos': forms.Textarea(attrs={'rows': 4}),
            'fecha_inicio': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'fecha_termino': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            'fecha_limite_inscripcion': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in ('fecha_inicio', 'fecha_termino', 'fecha_limite_inscripcion'):
            self.fields[campo].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']
        self.fields['profesores'].queryset = Usuario.objects.filter(
            rol=Usuario.Rol.PROFESOR
        ).order_by('first_name', 'username')

    def clean_cupos(self):
        cupos = self.cleaned_data['cupos']
        if self.instance.pk:
            ocupados = self.instance.cupos - cupos_disponibles(self.instance)
            if cupos < ocupados:
                raise forms.ValidationError(
                    'No puede ser menor que los cupos ocupados o reservados.'
                )
        return cupos


class InscripcionAdminForm(forms.Form):
    estudiante = forms.ModelChoiceField(queryset=Usuario.objects.none())
    curso = forms.ModelChoiceField(queryset=Curso.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ahora = timezone.now()
        self.fields['estudiante'].queryset = Usuario.objects.filter(
            rol=Usuario.Rol.ESTUDIANTE
        ).order_by('username')
        self.fields['curso'].queryset = Curso.objects.filter(
            estado=Curso.Estado.PUBLICADO,
            fecha_inicio__gt=ahora,
            fecha_limite_inscripcion__gte=ahora,
        ).order_by('fecha_inicio')
