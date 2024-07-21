from django.db.models import Max, Min # Importação para pegar o preco minimo e maximo
from django.core.mail import send_mail # codigo pronto do django para enviar emails 
from django.http import HttpResponse # codigo pronto do django para retornar respostas em http
import csv

def filtrar_produto(produtos, filtro):
    if filtro:
        if '-' in filtro:
            categoria, tipo = filtro.split('-')
            produtos = produtos.filter(categoria__slug=categoria, tipo__slug=tipo)
        else:
            produtos = produtos.filter(categoria__slug=filtro)
    return produtos


def minimo_maximo(produtos):
    minimo = 0
    maximo = 0
    if len(produtos) > 0:
        # o parametro aggregate agrupa todos os valores passados no parentese 
        minimo = list(produtos.aggregate(Min('preco')).values())[0] # a funcao "Min" junto do aggregate irá retornar o objeto com o menor valor dos produtos agrupados
        # para pegar o valor, como o aggregate retorna um objeto, temos que usar o .values() no final, 
        # transformar numa lista e pegar apenas o primeiro valor da lista com o [0]
        minimo = round(minimo, 2)

        maximo = list(produtos.aggregate(Max('preco')).values())[0] # forma de usar o "Max" 
        maximo = round(maximo, 2)
    
    return minimo, maximo


def ordenar_produtos(produtos, ordem):
    if ordem == 'menor-preco':
        produtos = produtos.order_by('preco') # para ordenar de acordo com algum campo usamos o order_by, para numeros, ou seja, DecimalField,
        # o padrao e de ordenar do menor para o maior
    elif ordem == 'maior-preco':
        produtos = produtos.order_by('-preco') # para ordenar do maior para o menor, se coloca um '-' logo antes do nome do campo
    elif ordem == 'mais-vendidos':
        lista_produtos = []
        for produto in produtos:
            lista_produtos.append((produto.total_vendas(), produto))
        print(lista_produtos)
        produtos = sorted(produtos, key=lambda produto: produto.total_vendas(), reverse=True)
    return produtos


def enviar_email(pedido):
    email = pedido.cliente.email
    assunto = f'Pedido n° {pedido.id} aprovado'
    mensagem = f'''Seu pedido foi aprovado
    Id do pedido: {pedido.id}
    Valor: {pedido.preco_total}
    Data de finalizacao: {pedido.data_finalizacao.strftime('%d/%m/%y')}'''
    remetente = 'neitzkerudilberto@gmail.com'
    send_mail(assunto, mensagem, remetente, [email])  


def exportar_csv(informacoes):
    colunas = informacoes.model._meta.fields
    nome_colunas = [coluna.name for coluna in colunas]
    
    resposta = HttpResponse(content_type='text/csv') # modo de pegar a resposta http usando content p/ informar que queremos um csv
    resposta["Content-Disposition"] = 'attachment; filename="export.csv"' # modo de dizer que o navegador devera fazer o download, 
    # filename da o nome do arquivo baixado

    criador_csv = csv.writer(resposta, delimiter=';')
    criador_csv.writerow(nome_colunas)
    for linha in informacoes.values_list(): # values_list() retorna uma lista de tuplas com valores dentro da tabela
        criador_csv.writerow(linha)

    return resposta