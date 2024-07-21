    const url = new URL(document.URL)
    const itens = document.getElementsByClassName('item-ordenar')

    for (i in itens){
        url.searchParams.set('ordem', itens[i].value);
        itens[i].value = url.href;
    }