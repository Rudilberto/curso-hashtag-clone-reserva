import mercadopago

public_key = 'TEST-873b862b-f35b-4526-b908-eb8bf4311ce7'

token = 'TEST-8469989083532345-052021-8bee556f4b5bf5dc0c96ef7622f7e3e8-420771914'

def criar_pagamento(itens_pedido, link):
    sdk = mercadopago.SDK(token)

    itens = []
    for item in itens_pedido:
        quantidade = int(item.quantidade)
        nome_produto = item.item_estoque.produto.nome
        preco_unitario = float(item.item_estoque.produto.preco)
        itens.append({
                "title": nome_produto,
                "quantity": quantidade,
                "unit_price": preco_unitario
            })

    preference_data = {
        "items": itens,

        "auto_return": 'all',

        "back_urls": {
                "success": link,
                "pending": link,
                "failure": link
                }
    }

    resposta = sdk.preference().create(preference_data)
    link_pagamento = resposta['response']['init_point']
    id_pagamento = resposta['response']['id']
    return link_pagamento, id_pagamento