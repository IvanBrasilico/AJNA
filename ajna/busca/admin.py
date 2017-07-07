from django.contrib import admin

# Register your models here.
from .models import FonteImagem, ConteinerEscaneado

admin.site.register(FonteImagem)

admin.site.register(ConteinerEscaneado)