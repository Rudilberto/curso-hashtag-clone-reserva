from django.urls import path  
from django.contrib.auth import views
from .views import *
# temos que importar o .views para usar as funcoes

# aqui nós definimos os links que teremos em nosso site passando os parametros:
# path('nome que tera no link', nomedafuncao, name='colocamos o mesmo nome da funcao')
# a funcao sera criada no arquivo views.py

urlpatterns = [
    path('', homepage, name='homepage'),
    path('loja/', loja, name='loja'),
    path('loja/<str:filtro>/', loja, name='loja'), # para criar um link dinamico usaremos o <str:link>
    path('produto/<int:id_produto>/', ver_produto, name='ver_produto'), # aqui criamos um link que so existe de forma dinamica
    path('produto/<int:id_produto>/<int:id_cor>/', ver_produto, name='ver_produto'),
    path('carrinho/', carrinho, name='carrinho'),
    path('checkout/', checkout, name='checkout'),

    path('finalizarpedido/<int:id_pedido>/', finalizar_pedido, name='finalizar_pedido'),
    path('finalizarpagamento/', finalizar_pagamento, name='finalizar_pagamento'),
    path('adicionarcarrinho/<int:id_produto>/', adicionar_carrinho, name='adicionar_carrinho'),
    path('removercarrinho/<int:id_produto>/', remover_carrinho, name='remover_carrinho'),
    path('adicionarendereco/', adicionar_endereco, name='adicionar_endereco'),

    path('criarconta/', criar_conta, name='criar_conta'),
    path('minhaconta/', minha_conta, name='minha_conta'),
    path('meuspedidos/', meus_pedidos, name='meus_pedidos'),
    path('pedidoaprovado/<int:id_pagamento>/', pedido_aprovado, name='pedido_aprovado'),
    
    path('fazerlogin/', fazer_login, name='fazer_login'),
    path('fazerlogout/', fazer_logout, name='fazer_logout'),

    path('gerenciarloja/', gerenciar_loja, name='gerenciar_loja'),
    path('exportarrelatorio/<str:relatorio>/', exportar_relatorio, name='exportar_relatorio'),

    path("password_change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/", views.PasswordChangeDoneView.as_view(), name="password_change_done"),
    
    path("password_reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

]