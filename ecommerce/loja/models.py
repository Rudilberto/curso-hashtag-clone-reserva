from django.db import models
from django.contrib.auth.models import User

# aqui criamos o banco de dados do projeto colocando sempre o models.Model como parameto da classe
# depois de adicionar qualquer classe aqui devemos adicionala tambem no arquivo admin.py

class Cliente(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True) # Charfield é um campo de texto
    email = models.CharField(max_length=200, null=True, blank=True) # os parametros null e blank indicam que o campo pode ser vazio
    telefone = models.CharField(max_length=200, null=True, blank=True)
    id_sessao = models.CharField(max_length=200, null=True, blank=True)
    usuario = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.email)
    

class Categoria(models.Model): # (masculino , feminino)
    nome = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True) # maneira de escrever links agradavelmente


    def __str__(self): # adicionamos esse metodo para no site aparecer o nome da categoria criada, ao inves de aparecer somento um Object
        return str(self.nome)


class Tipo(models.Model): # (camisa, bermuda, calçado)
    nome = models.CharField(max_length=200, null=True, blank=True)
    slug = models.CharField(max_length=200, null=True, blank=True)


    def __str__(self):
        return str(self.nome)


class Produto(models.Model):
    # mesmo nao criando aqui, o django ira criar automaticamento a variavel id = models.IntegerField que contém um numero unico a cada produto criado
    imagem = models.ImageField(null=True, blank=True)
    nome = models.CharField(max_length=200, null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(Categoria, null=True, blank=True, on_delete=models.SET_NULL) # permite usar outras classes
    tipo = models.ForeignKey(Tipo, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self): # tambem podemos passar um texto ao inves de um valor unico
        return f'Nome: {self.nome}, Categoria: {self.categoria}, Tipo: {self.tipo}, Preço: {self.preco}'
    

    def total_vendas(self):
        itens = ItensPedido.objects.filter(pedido__finalizado=True, item_estoque__produto=self.id)
        total = sum([item.quantidade for item in itens])
        return total


class Cor(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    codigo = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.nome)


class ItemEstoque(models.Model):
    produto = models.ForeignKey(Produto, null=True, blank=True, on_delete=models.SET_NULL)
    cor = models.ForeignKey(Cor, null=True, blank=True, on_delete=models.SET_NULL)
    tamanho = models.CharField(max_length=200, null=True, blank=True)
    quantidade = models.IntegerField(default=0)

    def __str__(self):
        return f'Nome: {self.produto.nome}, Cor: {self.cor.nome}, Tamanho: {self.tamanho}, Quantidade: {self.quantidade}'


class Endereco(models.Model):
    rua = models.CharField(max_length=400, null=True, blank=True)
    numero = models.IntegerField(default=0)
    complemento = models.CharField(max_length=200, null=True, blank=True)
    cep = models.CharField(max_length=200, null=True, blank=True)
    cidade = models.CharField(max_length=200, null=True, blank=True)
    estado = models.CharField(max_length=200, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Cliente: {self.cliente.nome}, Rua: {self.rua}, Número: {self.numero}, Cidade: {self.cidade}-{self.estado}'


class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.SET_NULL)
    finalizado = models.BooleanField(default=False)
    codigo_transacao = models.CharField(max_length=200, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, null=True, blank=True, on_delete=models.SET_NULL)
    data_finalizacao = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        if self.cliente.email:
            email = self.cliente.email
        else:
            email = 'Anônimo'
        return f'Cliente: {email}, Id-pedido: {self.id}, Finalizado: {self.finalizado}'
    
    @property
    def quantidade_total(self):
        itens_pedido = ItensPedido.objects.filter(pedido__id=self.id)
        return sum([item.quantidade for item in itens_pedido])

    @property # property faz com que usemos funcoes sem o () no final
    def preco_total(self):
        preco_pedido = ItensPedido.objects.filter(pedido__id=self.id)
        return sum([item.preco_total for item in preco_pedido])
    
    @property
    def itens(self):
        itens_pedido = ItensPedido.objects.filter(pedido__id=self.id)
        return itens_pedido


class ItensPedido(models.Model):
    item_estoque = models.ForeignKey(ItemEstoque, null=True, blank=True, on_delete=models.SET_NULL)
    quantidade = models.IntegerField(default=0)
    pedido = models.ForeignKey(Pedido, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Id-pedido: {self.pedido.id}, Produto: {self.item_estoque.produto.nome} {self.item_estoque.cor.nome} {self.item_estoque.tamanho}'
    
    @property # property faz com que usemos funcoes sem o () no final
    def preco_total(self):
        preco_total = self.quantidade * self.item_estoque.produto.preco
        return preco_total


class Banner(models.Model):
    imagem = models.ImageField(null=True, blank=True)
    link_destino = models.CharField(max_length=400, null=True, blank=True)
    ativo = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.link_destino} - ativo: {self.ativo}'
    

class Pagamento(models.Model):
    id_pagamento = models.CharField(max_length=400, null=True, blank=True)
    pedido = models.ForeignKey(Pedido, null=True, blank=True, on_delete=models.CASCADE)
    aprovado = models.BooleanField(default=False) 

    def __str__(self):
        return f'{self.id_pagamento} - aprovado: {self.aprovado}'