# aqui criaremos uma função que estara disponivel em todos os htmls por meio das settings.py em context_processors
# sera basicamente um retorno que sera um contexto usavel em todos os htmls
 
from .models import Pedido, ItensPedido, Cliente, Categoria, Tipo

def carrinho(request):
    quantidades_produtos_carrinho = 0
    if request.user.is_authenticated: # o .user esta existe automaticamente em qualquer função que tenho o request 
        cliente = request.user.cliente
    else:
        if request.COOKIES.get('id_sessao'): # request.COOKIES retorna um dicionario com todos os cookies do navegador
            id_sessao = request.COOKIES.get('id_sessao')
            cliente, criado = Cliente.objects.get_or_create(id_sessao=id_sessao)
        else:
            return {'quantidade_produtos_carrinho': quantidades_produtos_carrinho}
    pedido, criado = Pedido.objects.get_or_create(cliente=cliente, finalizado=False) # get_or_create é um parametro do django que
    # retorna 2 variaveis, 1 - pega a informação passada, 2 - retorna True oo False caso o django tenha que criar a informação
    itens_pedido = ItensPedido.objects.filter(pedido=pedido)
    for item in itens_pedido:
        quantidades_produtos_carrinho += item.quantidade
    return {'quantidade_produtos_carrinho': quantidades_produtos_carrinho}

def categorias_tipos(request):
    categorias_navegacao = Categoria.objects.all()
    tipos_navegacao = Tipo.objects.all()
    return {'categorias_navegacao': categorias_navegacao, 'tipos_navegacao': tipos_navegacao}

def membros_equipe(request):
    equipe = False
    if request.user.is_authenticated:
        if request.user.groups.filter(name='equipe').exists():
            equipe = True        
    return {'equipe': equipe}