from django.contrib import admin
from .models import *

# aqui colocamos as classes criadas no nosso arquivo models.py e apos isso usaremos o comando makemigrations e migrate

admin.site.register(Cliente)
admin.site.register(Tipo)
admin.site.register(Produto)
admin.site.register(ItemEstoque)
admin.site.register(Endereco)
admin.site.register(ItensPedido)
admin.site.register(Pedido)
admin.site.register(Categoria)
admin.site.register(Banner)
admin.site.register(Cor)
admin.site.register(Pagamento)