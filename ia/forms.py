from django import forms

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario


class ConfiguracaoIAForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoIA
        exclude = ["atualizada_em"]
        widgets = {
            "api_key": forms.PasswordInput(render_value=False),
            "temperatura": forms.NumberInput(
                attrs={"step": "0.01", "min": "0", "max": "2"}
            ),
        }


class ConfiguracaoIAUsuarioForm(forms.ModelForm):
    class Meta:
        model = ConfiguracaoIAUsuario
        fields = ["usuario", "ia_ligada", "limite_tokens", "observacao"]
