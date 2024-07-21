from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from .api_mercadopago import criar_pagamento
from .utils import *
import uuid # biblioteca padrao do python que gera ids aleatorios sem repetir-los
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email   
from django.core.exceptions import ValidationError
from datetime import datetime

# Create your views here.

# aqui criamos as funcoes que usaremos no urls.py que no final nos retornara um arquivo html
# sempre colocaremos o 'request' como parametro da funcao e o retorno ficara no formato render(request, 'arquivohtml.html')
def homepage(request):
    # ao usar uma classe do models.py, podemos usar 4 metodos do django, o all(), filter(), first() e order_by()
    banners = Banner.objects.filter(ativo=True) # para usar o filter o modo mais basico seria indicar a variavel do objeto do banco 
    # de dados do arquivo models.py e ver se seu valor é igual a alguma coisa ex: ativo=True sendo que ativo e uma variavel do Banner()
    context = {'banners': banners} # a variavel context precisa ser um diiconario que podera ser acessado em nossos htmls
    return render(request, 'homepage.html', context)


def loja(request, filtro=None): # Passaremos aqui o valor padrao para o link dinamico do urls.py
    produtos = Produto.objects.filter(ativo=True)  
    produtos = filtrar_produto(produtos, filtro)
    if request.method == 'POST':
        dados = request.POST.dict() # modo de pegar os dados do formulario
        # gte = maior ou igual, lte = menor ou igual
        produtos = produtos.filter(preco__gte=dados.get('preco_minimo'), preco__lte=dados.get('preco_maximo'))
        if 'tamanho' in dados:
            itens = ItemEstoque.objects.filter(produto__in=produtos, tamanho=dados.get('tamanho'))
            ids_produtos = itens.values_list('produto', flat=True).distinct() 
            produtos = produtos.filter(id__in=ids_produtos)
        if 'tipo' in dados:
            produtos = produtos.filter(tipo__slug=dados.get('tipo'))
        if 'categoria' in dados:
            produtos = produtos.filter(categoria__slug=dados.get('categoria'))

    itens = ItemEstoque.objects.filter(produto__gt=0, produto__in=produtos)
    tamanhos = itens.values_list('tamanho', flat=True).distinct() 
    # .values_list() nos dará uma lista de tuplas com o resultado e o distinct() irá retirar os resultados repetidos
    # flat fara o unpacking automatico para ao inves de tuplas o values_list nos dar o resultado direto
    ids_categoria = produtos.values_list('categoria', flat=True).distinct()
    categorias = Categoria.objects.filter(id__in=ids_categoria)
    
    minimo, maximo = minimo_maximo(produtos)

    ordem = request.GET.get('ordem', 'menor-preco') # request.GET sempre esta disponivel e serve para pegarmos a ordenação do site, sendo ('parametro', 'default')
    # nessa situacao estamos pegando a 'ordem' que e o padrao de ordenação e o 'menor-preco' sera a ordenação padrao
    produtos = ordenar_produtos(produtos, ordem)

    context = {'produtos': produtos, 'tamanhos': tamanhos, 'minimo': minimo, 'maximo': maximo, 'categorias': categorias} 
    # um contexto é um dicionario que sera lido pelo django acessando com um {{ var }} no nosso html
    return render(request, 'loja.html', context)


def ver_produto(request, id_produto, id_cor=None):
    tem_estoque = False
    cores = {}
    tamanhos = {}
    cor_selecionada = None
    if id_cor:
        cor_selecionada = Cor.objects.get(id=id_cor)
    produto = Produto.objects.get(id=id_produto) # usando o get() podemos pegar um valor apenas obs: o campo id e criado pelo django 
    itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0) # __gt e uma funcionalidade do django que indica Greater Than
    if len(itens_estoque) > 0:
        tem_estoque = True
        cores = {item.cor for item in itens_estoque}
        if id_cor:
            itens_estoque = ItemEstoque.objects.filter(produto=produto, quantidade__gt=0, cor__id=id_cor)
            tamanhos = {item.tamanho for item in itens_estoque}
    similares = Produto.objects.filter(categoria__id=produto.categoria.id, tipo__id=produto.tipo.id).exclude(id=produto.id  )[:4]

    context = {'produto': produto, 'tem_estoque': tem_estoque, 'cores': cores, 'tamanhos': tamanhos, 'cor_selecionada': cor_selecionada,'similares': similares }
    
    return render(request, 'ver_produto.html', context)


def adicionar_carrinho(request, id_produto):
    if request.method == 'POST' and id_produto:
        dados = request.POST.dict() # modo de pegar os dados do formulario
        tamanho = dados.get('tamanho') 
        id_cor = dados.get('cor') 
        if not tamanho:
            redirect('loja')
        resposta = redirect('carrinho')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
                id_sessao = request.COOKIES.get('id_sessao')
            else:
                id_sessao = str(uuid.uuid4()) # biblioteca de numeros aleatorios importada
                resposta.set_cookie(key='id_sessao', value=id_sessao, max_age=60*60*24*30) # set_cookie nos permite adicionar cookies ao navegador
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=id_produto, tamanho=tamanho, cor__id=id_cor)
        item_pedido, criado = ItensPedido.objects.get_or_create(item_estoque=item_estoque, pedido=pedido)
        item_pedido.quantidade += 1
        item_pedido.save() # sempre ao alterar um valor de variavel do banco de dados, temos que usar o .save()
        return resposta
    else:
        return redirect('loja')
    

def remover_carrinho(request, id_produto):
    if request.method == 'POST' and id_produto:
        dados = request.POST.dict()
        tamanho = dados.get('tamanho') 
        id_cor = dados.get('cor') 
        if not tamanho:
            redirect('loja')
        if request.user.is_authenticated:
            cliente = request.user.cliente
        else:
            if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
                id_sessao = request.COOKIES.get('id_sessao')
            else:
                return redirect('loja')
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False)
        item_estoque = ItemEstoque.objects.get(produto__id=id_produto, tamanho=tamanho, cor__id=id_cor)
        # filtro avançado django: ao usar variavel de classe(categoria) junto de 2 underlines ( __ ) e apos uma outra variavel de classe ( nome )
        # com isso o django irá procurar se alguma variavel 'nome' tem o valor igual ao parametro passado ex categoria__nome=nome_categoria
        item_pedido, criado = ItensPedido.objects.get_or_create(item_estoque=item_estoque, pedido=pedido)
        item_pedido.quantidade -= 1
        item_pedido.save() # sempre ao alterar um valor de variavel do banco de dados, temos que usar o .save()
        if item_pedido.quantidade <= 0:
            item_pedido.delete()
        return redirect('carrinho')
    else:
        return redirect('loja')


def carrinho(request):
    if request.user.is_authenticated: 
        cliente = request.user.cliente  
    else: 
        if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
            id_sessao = request.COOKIES.get('id_sessao')
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            context = {'cliente_existente': False,'itens_pedido': None, 'pedido': None}
            return render(request, 'carrinho.html', context)
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False) # get_or_create é um parametro do django que
    # retorna 2 variaveis, 1 - pega a informação passada, 2 - retorna True oo False caso o django tenha que criar a informação
    itens_pedido = ItensPedido.objects.filter(pedido=pedido)
    context = {'cliente_existente': True,'itens_pedido': itens_pedido, 'pedido': pedido}
    return render(request, 'carrinho.html', context)


def checkout(request):
    if request.user.is_authenticated: 
        cliente = request.user.cliente
    else: 
        if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
            id_sessao = request.COOKIES.get('id_sessao')
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return render('loja')
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False) # get_or_create é um parametro do django que
    # retorna 2 variaveis, 1 - pega a informação passada, 2 - retorna True oo False caso o django tenha que criar a informação
    enderecos = Endereco.objects.filter(cliente=cliente)
    context = {'pedido': pedido, 'enderecos': enderecos}
    return render(request, 'checkout.html', context)


def finalizar_pedido(request, id_pedido):
    erro = None
    if request.method == 'POST':
        dados = request.POST.dict()
        total = dados.get('total')
        total = float(total.replace(',','.'))

        pedido = Pedido.objects.get(id=id_pedido)
        if total != float(pedido.preco_total):
            erro = 'preco'  

        if not 'endereco' in dados:
            erro = 'endereco'
        else:
            id_endereco = dados.get('endereco')
            endereco = Endereco.objects.get(id=id_endereco)
            pedido.endereco = endereco
        if not request.user.is_authenticated:
            email = dados.get('email')
            try:
                validate_email(email)
            except ValidationError:
                erro = 'email'

            if not erro:
                clientes = Cliente.objects.filter(email=email)
                if clientes:
                    pedido.cliente = clientes[0]
                else:
                    pedido.cliente.email = email

        codigo_transacao = f'{pedido.id}-{datetime.now().timestamp()}'
        pedido.codigo_transacao = codigo_transacao
        pedido.save()
        if erro:
            enderecos = Endereco.objects.filter(cliente=pedido.cliente)
            context = {'erro': erro, 'pedido': pedido, 'enderecos': enderecos}
            return render(request, 'checkout.html', context)
        else:
            itens_pedido = ItensPedido.objects.filter(pedido=pedido)
            link = request.build_absolute_uri(reverse('finalizar_pagamento'))
            link_pagamento, id_pagamento = criar_pagamento(itens_pedido, link)
            print(link_pagamento)
            pagamento = Pagamento.objects.create(id_pagamento=id_pagamento, pedido=pedido)
            pagamento.save()
            return redirect(link_pagamento)
    else:
        return redirect('loja')
    
def finalizar_pagamento(request):
    # {'collection_id': '1323358043', 'collection_status': 'approved', 'payment_id': '1323358043', 'status': 'approved', 'external_reference': 'null', 'payment_type': 'credit_card', 'merchant_order_id': '18959738871', 'preference_id': '420771914-448cc7ca-9ae9-49b8-a9ec-a6848f8b9d2d', 'site_id': 'MLB', 'processing_mode': 'aggregator', 'merchant_account_id': 'null'}
    dados = request.GET.dict()
    status = dados.get('status')
    id_pagamento = dados.get('preference_id')
    if status == 'approved':
        pagamento = Pagamento.objects.get(id_pagamento=id_pagamento)
        pagamento.aprovado = True
        pedido = pagamento.pedido
        pedido.finalizado = True
        pedido.data_finalizacao = datetime.now()
        pagamento.save()
        pedido.save()
        enviar_email(pedido)  

        if request.user.is_authenticated:
            return redirect('meus_pedidos')
        else:
            redirect('pedido_aprovado', pedido.id)
    else:
        return redirect('checkout')

    return redirect('loja')


def pedido_aprovado(request, id_pedido):
    pedido = Pedido.objects.get(id=id_pedido)
    context = {'pedido': pedido}
    return render(request, 'pedido_aprovado.html', context)


def adicionar_endereco(request):
    if request.method == 'POST':
        if request.user.is_authenticated: 
            cliente = request.user.cliente
        else: 
            if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
                id_sessao = request.COOKIES.get('id_sessao')
                cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
            else:
                return render('loja')
        dados = request.POST.dict()
        endereco = Endereco.objects.create(cliente=cliente, cidade=dados.get('cidade'), estado=dados.get('estado'),rua=dados.get('rua'), 
                                           complemento=dados.get('complemento'),numero=int(dados.get('numero')), cep=dados.get('cep'))
        endereco.save()
        return redirect('checkout')
    else:
        context = {}
        return render(request, 'adicionar_endereco.html', context)
    

def criar_conta(request):
    erro = None
    if request.user.is_authenticated:
        return redirect('loja')
    if request.method == 'POST':
        dados = request.POST.dict()
        email = dados.get('email')
        senha = dados.get('senha')
        confirmacao_senha = dados.get('confirmacao_senha')
        if not email or not senha or not confirmacao_senha:
            erro = 'preenchimento'
        else:
            try:
                validate_email(email)
            except ValidationError:
                erro = 'email_invalido'
            if senha == confirmacao_senha:
                usuario, criado = User.objects.get_or_create(username=email, email=email)
                if not criado:
                    erro = 'usuario_existente'
                else:
                    usuario.set_password(senha)
                    usuario.save()
                    usuario = authenticate(request, username=email, password=senha) 
                    login(request, usuario) 

                    if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
                        id_sessao = request.COOKIES.get('id_sessao')
                        cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)

                    else:
                        cliente, criado = Cliente.objects.get_or_create(email=email)
                    cliente.usuario = usuario
                    cliente.email = email
                    cliente.save()
                    return redirect('loja')
            else:
                erro = 'senhas_diferentes'

    context = {'erro': erro}
    return render(request, 'usuario/criar_conta.html', context)


@login_required
def minha_conta(request):
    cliente = request.user.cliente
    erro = None
    alterado = False
    if request.method == 'POST':
        dados = request.POST.dict()
        if 'senha_atual' in dados:
            senha_atual = dados.get('senha_atual')
            nova_senha = dados.get('nova_senha')
            nova_senha_confirmacao = dados.get('nova_senha_confirmacao')
            if nova_senha == nova_senha_confirmacao and nova_senha_confirmacao != '':
                usuario = authenticate(request, username=request.user.email, password=senha_atual)
                if usuario:
                    usuario.set_password = nova_senha
                    usuario.save()
                    alterado = True
                else:
                    erro = 'senha_incorreta'
            else:
                erro = 'senhas_diferentes'

        elif 'email' in dados:
            nome = dados.get('nome')
            email = dados.get('email')
            telefone = dados.get('telefone')
            if not email:
                erro = 'email_vazio'
                context = {'erro': erro, 'alterado': alterado}
                return render(request, 'usuario/minha_conta.html', context)
            if email != request.user.email:
                usuario = User.objects.filter(email=email)
                if len(usuario) > 0:
                    erro = 'email_existente'
            if not erro:
                cliente = request.user.cliente
                cliente.email = email
                request.user.email = email
                request.user.username = email
                cliente.nome = nome
                cliente.telefone = telefone
                cliente.save()
                request.user.save()
                alterado = True
        else:
            erro = 'formulario_invalido'
    context = {'erro': erro, 'alterado': alterado}
    return render(request, 'usuario/minha_conta.html', context)


@login_required
def meus_pedidos(request):
    cliente = request.user.cliente  
    pedidos = Pedido.objects.filter(finalizado=True, cliente=cliente).order_by('-data_finalizacao')
    context = {'pedidos': pedidos}
    return render(request, 'usuario/meus_pedidos.html', context)


def fazer_login(request):
    erro = False
    if request.user.is_authenticated:
        return redirect('loja')
    if request.method == 'POST':
        dados = request.POST.dict()
        if 'email' in dados and 'senha' in dados:
            email = dados.get('email')
            senha = dados.get('senha')
            usuario = authenticate(request, username=email, password=senha)
            if usuario:
                login(request, usuario)
                return redirect('loja')   
            else:
                erro = True  
        else:
            erro = True
    context = {'erro': erro}
    return render(request, 'usuario/login.html', context)


@login_required
def fazer_logout(request):
    logout(request)
    return redirect('fazer_login')


@login_required
def gerenciar_loja(request):
    if request.user.groups.filter(name='equipe').exists():
        pedidos_finalizados = Pedido.objects.filter(finalizado=True)
        faturamento = sum(float(pedido.preco_total) for pedido in pedidos_finalizados)
        produtos_vendidos = sum(int(pedido.quantidade_total) for pedido in pedidos_finalizados)
        quantidade_pedidos = sum(float(pedido.preco_total) for pedido in pedidos_finalizados)
        context = {'faturamento': faturamento, 'produtos_vendidos': produtos_vendidos, 'quantidade_pedidos': quantidade_pedidos}
        return render(request, 'interno/gerenciar_loja.html', context)
    else:
        redirect('loja')


@login_required
def exportar_relatorio(request, relatorio):
    if request.user.groups.filter(name='equipe').exists():
        if relatorio == 'pedido':
            informacoes = Pedido.objects.filter(finalizado=True)
        elif relatorio == 'cliente':
            informacoes = Cliente.objects.all()
        elif relatorio == 'endereco':
            informacoes = Endereco.objects.all()
        return exportar_csv(informacoes)
    
    else:
        redirect('loja')

    