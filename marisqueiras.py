# ENTREGA: IMPLEMENTAÇÃO DE CLASSES E MÉTODOS - PROJETO MARISQUEIRAS DA ILHA

QUANTIDADE_MINIMA = 25  

STATUS_ENTREGA = ["em preparo", "em curso", "finalizado"]
# Antes de aceitar, o pedido fica "realizado". Se a empresa não aceitar, ele fica
# "rejeitado" ou "ajuste solicitado" (fluxo do PDF 1: aceitar, rejeitar ou solicitar ajuste).


def validar_cnpj(cnpj):
    """O id das empresas é o CNPJ. Tira pontos, barra e traço e confere os 14 números."""
    numeros = ""
    for caractere in cnpj:
        if caractere.isdigit():
            numeros = numeros + caractere
    if len(numeros) != 14:
        raise ValueError("O CNPJ deve ter 14 números.")
    return numeros


def calcular_media(marisqueira):
    """Média das notas da empresa (0 se ela ainda não tem avaliações)."""
    if len(marisqueira.avaliacoes) == 0:
        return 0
    soma = 0
    for avaliacao in marisqueira.avaliacoes:
        soma = soma + avaliacao.nota
    return soma / len(marisqueira.avaliacoes)


def preco_do_produto(produto):
    return produto.preco


def media_do_produto(produto):
    return calcular_media(produto.empresa)


class Empresa:
    def __init__(self, nome, localizacao):
        if nome.strip() == "":
            raise ValueError("O nome da empresa é obrigatório.")
        if localizacao.strip() == "":
            raise ValueError("A localização é obrigatória.")
        self.nome = nome.strip()
        self.localizacao = localizacao.strip()


class Produto:
    contador = 0  # usado para gerar o id_produto

    def __init__(self, empresa, nome, categoria, preco, quantidade_disponivel, fotografia=""):
        # todos os dados são obrigatórios, exceto a fotografia
        if nome.strip() == "":
            raise ValueError("O nome do produto é obrigatório.")
        if categoria != "fresco" and categoria != "congelado":
            raise ValueError("A categoria deve ser 'fresco' ou 'congelado'.")
        if preco <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        if quantidade_disponivel < QUANTIDADE_MINIMA:
            raise ValueError("A quantidade disponível deve ser de pelo menos 25 kg.")
        Produto.contador = Produto.contador + 1
        self.id_produto = Produto.contador
        self.empresa = empresa
        self.nome = nome.strip()
        self.categoria = categoria
        self.preco = preco
        self.quantidade_disponivel = quantidade_disponivel 
        self.fotografia = fotografia  

    def verificar_disponibilidade(self, quantidade):
        """Devolve True se a quantidade pedida não ultrapassa a disponível."""
        return quantidade > 0 and quantidade <= self.quantidade_disponivel

    def atualizar_quantidade(self, nova_quantidade):
        if nova_quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        self.quantidade_disponivel = nova_quantidade


class ItemPedido:
    def __init__(self, id_pedido, produto, quantidade):
        self.id_pedido = id_pedido
        self.id_produto = produto.id_produto
        self.produto = produto
        self.quantidade = quantidade  

    def validar_quantidade(self):
        """A quantidade mínima é de 25 kg para cada produto."""
        if self.quantidade < QUANTIDADE_MINIMA:
            raise ValueError(f"'{self.produto.nome}': a quantidade mínima é de 25 kg.")

    def verificar_disponibilidade(self):
        return self.produto.verificar_disponibilidade(self.quantidade)


class Pedido:
    contador = 0  

    def __init__(self, comprador, marisqueira, endereco_entrega, tempo_entrega):
        if endereco_entrega.strip() == "":
            raise ValueError("O endereço de entrega é obrigatório.")
        if str(tempo_entrega).strip() == "":
            raise ValueError("O tempo de entrega é obrigatório.")
        Pedido.contador = Pedido.contador + 1
        self.id_pedido = Pedido.contador
        self.comprador = comprador
        self.marisqueira = marisqueira
        self.endereco_entrega = endereco_entrega.strip()
        self.tempo_entrega = tempo_entrega
        self.status_pedido = "realizado"
        self.itens = []

    def adicionar_item(self, produto, quantidade):
        # um pedido não pode reunir produtos de empresas diferentes
        if produto.empresa != self.marisqueira:
            raise ValueError("Um pedido não pode ter produtos de empresas diferentes.")
        # o mesmo produto duas vezes poderia ultrapassar o estoque somando os itens
        for item in self.itens:
            if item.produto == produto:
                raise ValueError(f"'{produto.nome}' já está neste pedido.")

        item = ItemPedido(self.id_pedido, produto, quantidade)
        item.validar_quantidade()
        # a quantidade solicitada não pode ultrapassar a disponível
        if not item.verificar_disponibilidade():
            raise ValueError(f"'{produto.nome}': quantidade indisponível "
                             f"(disponível: {produto.quantidade_disponivel} kg).")
        self.itens.append(item)


class Avaliacao:
    contador = 0  # usado para gerar o id_avaliacao

    def __init__(self):
        Avaliacao.contador = Avaliacao.contador + 1
        self.id_avaliacao = Avaliacao.contador
        self.nota = 0

    def registrar_nota(self, nota):
        if nota < 1 or nota > 5:
            raise ValueError("A nota deve ser de 1 a 5 estrelas.")
        self.nota = nota


class EmpresaMarisqueira(Empresa):
    def __init__(self, cnpj, nome, localizacao):
        super().__init__(nome, localizacao)
        self.id_empresa_marisqueira = validar_cnpj(cnpj)
        self.produtos = []
        self.pedidos = []
        self.avaliacoes = []

    def cadastrar_produto(self, nome, categoria, preco, quantidade_disponivel, fotografia=""):
        produto = Produto(self, nome, categoria, preco, quantidade_disponivel, fotografia)
        self.produtos.append(produto)
        return produto

    def alterar_quantidade(self, produto, nova_quantidade):
        if produto.empresa != self:
            raise ValueError("Você só pode alterar os seus próprios produtos.")
        if nova_quantidade < QUANTIDADE_MINIMA:
            raise ValueError("A quantidade informada deve ser de pelo menos 25 kg.")
        produto.atualizar_quantidade(nova_quantidade)

    def receber_pedido(self, pedido):
        if pedido.marisqueira != self:
            raise ValueError("Este pedido é de outra empresa.")
        self.pedidos.append(pedido)

    def aceitar_pedido(self, pedido):
        if pedido not in self.pedidos:
            raise ValueError("Este pedido não foi recebido por esta empresa.")
        if pedido.status_pedido != "realizado" and pedido.status_pedido != "ajuste solicitado":
            raise ValueError(f"O pedido já está '{pedido.status_pedido}'.")
        # confere o estoque de novo, pois ele pode ter mudado desde o pedido
        for item in pedido.itens:
            if not item.verificar_disponibilidade():
                raise ValueError(f"'{item.produto.nome}': quantidade não disponível mais.")
        # desconta do estoque
        for item in pedido.itens:
            restante = item.produto.quantidade_disponivel - item.quantidade
            item.produto.atualizar_quantidade(restante)
        pedido.status_pedido = "em preparo"

    def rejeitar_pedido(self, pedido):
        if pedido not in self.pedidos:
            raise ValueError("Este pedido não foi recebido por esta empresa.")
        if pedido.status_pedido != "realizado" and pedido.status_pedido != "ajuste solicitado":
            raise ValueError(f"O pedido já está '{pedido.status_pedido}'.")
        pedido.status_pedido = "rejeitado"

    def solicitar_ajuste(self, pedido):
        if pedido not in self.pedidos:
            raise ValueError("Este pedido não foi recebido por esta empresa.")
        if pedido.status_pedido != "realizado" and pedido.status_pedido != "ajuste solicitado":
            raise ValueError(f"O pedido já está '{pedido.status_pedido}'.")
        pedido.status_pedido = "ajuste solicitado"

    def atualizar_status_entrega(self, pedido, novo_status):
        if pedido not in self.pedidos:
            raise ValueError("Este pedido não foi recebido por esta empresa.")
        if pedido.status_pedido not in STATUS_ENTREGA:
            raise ValueError("Só dá para atualizar o status de um pedido que já foi aceito.")
        if novo_status not in STATUS_ENTREGA:
            raise ValueError("Status inválido. Use: em preparo, em curso ou finalizado.")
        pedido.status_pedido = novo_status


class EmpresaCompradora(Empresa):
    def __init__(self, cnpj, nome, localizacao):
        super().__init__(nome, localizacao)
        self.id_empresa_compradora = validar_cnpj(cnpj)
        self.pedidos = []

    def consultar_produtos(self, marisqueiras, nome="", categoria="", localizacao="",
                           empresa="", avaliacao_minima=0, ordenar_por=""):
        """Busca produtos. Campo vazio = não filtra.

        ordenar_por: "menor_preco", "maior_preco", "melhor_avaliacao" ou "proximidade".
        """
        resultado = []
        for m in marisqueiras:
            if localizacao != "" and localizacao.lower() not in m.localizacao.lower():
                continue
            if empresa != "" and empresa.lower() not in m.nome.lower():
                continue
            if calcular_media(m) < avaliacao_minima:
                continue
            for p in m.produtos:
                if nome != "" and nome.lower() not in p.nome.lower():
                    continue
                if categoria != "" and p.categoria != categoria:
                    continue
                resultado.append(p)

        if ordenar_por == "menor_preco":
            resultado.sort(key=preco_do_produto)
        elif ordenar_por == "maior_preco":
            resultado.sort(key=preco_do_produto, reverse=True)
        elif ordenar_por == "melhor_avaliacao":
            resultado.sort(key=media_do_produto, reverse=True)
        elif ordenar_por == "proximidade":
            # modelagem simples: empresas na mesma localização do comprador vêm primeiro
            perto = []
            longe = []
            for p in resultado:
                if p.empresa.localizacao.lower() == self.localizacao.lower():
                    perto.append(p)
                else:
                    longe.append(p)
            resultado = perto + longe
        return resultado

    def comparar_produtos(self, produtos):
        if len(produtos) < 2:
            raise ValueError("Escolha pelo menos dois produtos para comparar.")
        print("\nCOMPARAÇÃO DE PRODUTOS")
        for p in produtos:
            print("-" * 35)
            print("Produto:", p.nome, f"({p.categoria})")
            print("Empresa:", p.empresa.nome)
            print("Localização:", p.empresa.localizacao)
            print(f"Preço: R$ {p.preco:.2f}")
            if p.quantidade_disponivel == 0:
                print("Disponível: indisponível")
            else:
                print("Disponível:", p.quantidade_disponivel, "kg")
            media = calcular_media(p.empresa)
            if media == 0:
                print("Avaliação: sem avaliações")
            else:
                print(f"Avaliação: {media:.1f} estrelas")

    def realizar_pedido(self, marisqueira, itens, endereco_entrega, tempo_entrega):
        """itens é uma lista de pares (produto, quantidade)."""
        pedido = Pedido(self, marisqueira, endereco_entrega, tempo_entrega)
        for produto, quantidade in itens:
            pedido.adicionar_item(produto, quantidade)  # valida cada item
        marisqueira.receber_pedido(pedido)
        self.pedidos.append(pedido)
        return pedido

    def avaliar_empresa(self, pedido, nota):
        if pedido.comprador != self:
            raise ValueError("Você só pode avaliar pedidos que você fez.")
        # a avaliação é feita após a compra (pedido aceito)
        if pedido.status_pedido not in STATUS_ENTREGA:
            raise ValueError("A avaliação só é possível depois da compra (pedido aceito).")
        avaliacao = Avaliacao()
        avaliacao.registrar_nota(nota)
        pedido.marisqueira.avaliacoes.append(avaliacao)
        return avaliacao