from django.contrib import admin

# Register your models here.
from .models import FonteImagem, ConteinerEscaneado, Agendamento

admin.site.register(FonteImagem)

admin.site.register(ConteinerEscaneado)


admin.site.register(Agendamento)
