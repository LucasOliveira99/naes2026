from django.contrib import admin
from django import forms

from .models import ConfiguracaoIA, ConfiguracaoIAUsuario, ConsumoIA, RequisicaoIA


class ConfiguracaoIAAdminForm(forms.ModelForm):
	class Meta:
		model = ConfiguracaoIA
		fields = "__all__"
		widgets = {"api_key": forms.PasswordInput(render_value=False)}


@admin.register(ConfiguracaoIA)
class ConfiguracaoIAAdmin(admin.ModelAdmin):
	form = ConfiguracaoIAAdminForm
	list_display = ["provedor", "acesso", "modelo", "atualizada_em"]
	exclude = ["atualizada_em"]

	def has_module_permission(self, request):
		return request.user.is_superuser

	def has_view_permission(self, request, obj=None):
		return request.user.is_superuser

	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser

	def has_add_permission(self, request):
		return request.user.is_superuser

	def has_delete_permission(self, request, obj=None):
		return False


@admin.register(ConfiguracaoIAUsuario)
class ConfiguracaoIAUsuarioAdmin(admin.ModelAdmin):
	list_display = ["usuario", "ia_ligada", "limite_tokens", "atualizada_em"]
	list_filter = ["ia_ligada"]

	def has_module_permission(self, request):
		return request.user.is_superuser

	def has_view_permission(self, request, obj=None):
		return request.user.is_superuser

	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser


@admin.register(ConsumoIA)
class ConsumoIAAdmin(admin.ModelAdmin):
	list_display = ["usuario", "mes", "tokens_total", "custo_estimado"]
	list_filter = ["mes"]
	readonly_fields = [field.name for field in ConsumoIA._meta.fields]

	def has_module_permission(self, request):
		return request.user.is_superuser

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


@admin.register(RequisicaoIA)
class RequisicaoIAAdmin(admin.ModelAdmin):
	list_display = ["criada_em", "usuario", "finalidade", "situacao", "tokens_total"]
	list_filter = ["situacao", "finalidade", "origem"]
	readonly_fields = [field.name for field in RequisicaoIA._meta.fields]

	def has_module_permission(self, request):
		return request.user.is_superuser

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False
