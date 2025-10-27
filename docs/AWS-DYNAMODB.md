# DynamoDB: Guia Definitivo para Performance e Escalabilidade NoSQL

**Versão 2.0: Revisado, expandido e com padrões de design avançados.**

---

## 0. TL;DR (Resumo Rápido)

*   **O que é?** Banco de dados NoSQL da AWS, totalmente gerenciado, feito para velocidade (latência de milissegundos) e escala massiva.
*   **Quando usar?** Aplicações que precisam de respostas rápidas e consistentes, mesmo com milhões de usuários (e-commerce, jogos, IoT, feeds de redes sociais). Ideal quando você conhece seus padrões de acesso aos dados.
*   **Como funciona?** Pense em chave-valor. Você busca dados usando uma **Chave Primária**. Não há `JOINs` como em SQL. O design dos dados é focado em *como* você vai ler os dados.
*   **Operações principais:**
    *   `put_item`: Cria/sobrescreve um item.
    *   `get_item`: Lê um item pela sua chave (super rápido).
    *   `update_item`: Modifica um item existente.
    *   `delete_item`: Remove um item.
    *   `query`: Busca um conjunto de itens com a mesma chave de partição (eficiente).
    *   `scan`: Varre a tabela inteira (lento, caro, evite em produção).
*   **Regra de Ouro:** Modele seus dados para usar `query`, não `scan`. Se precisar de novos padrões de busca, crie um **Índice Secundário Global (GSI)**.

---

## 1. O que é o Amazon DynamoDB?

O Amazon DynamoDB é um serviço de banco de dados NoSQL totalmente gerenciado pela AWS, projetado para oferecer **performance de milissegundos de um dígito em qualquer escala**. É a solução ideal para aplicações modernas que exigem baixa latência e alta escalabilidade, como apps móveis, jogos, plataformas de publicidade, IoT e sistemas de e-commerce.

**Analogia do Mundo Real:**

*   **Banco de Dados SQL (RDS):** Uma biblioteca com um catálogo de fichas super organizado. Para encontrar um livro, você pode cruzar informações complexas (autor, gênero, ano). É poderoso, mas pode ser lento se a busca for complexa.
*   **DynamoDB:** Um depósito gigante com um sistema de endereçamento perfeito. Cada item tem um "endereço" único (sua chave primária). Se você sabe o endereço, a entrega é quase instantânea. Tentar encontrar algo sem o endereço (usando `scan`) significa procurar em cada prateleira do depósito.

### Principais Características:

*   **Totalmente Gerenciado:** A AWS cuida de tudo: provisionamento de hardware, patches de segurança, replicação, backups e escalabilidade. Você foca no seu código.
*   **Performance Massiva em Escala:** Latência consistente de milissegundos, mesmo com milhões de requisições por segundo.
*   **Flexibilidade de Esquema (Schemaless):** Sendo NoSQL, não exige um esquema fixo. Cada item (linha) pode ter atributos (colunas) diferentes, permitindo evoluir sua aplicação sem migrações de esquema complexas.
*   **Segurança Robusta:** Criptografia em repouso e em trânsito, controle de acesso granular com IAM e integração com Virtual Private Cloud (VPC).
*   **Modelo de Preços Flexível:**
    *   **On-Demand (Sob Demanda):** Pague por requisição. Perfeito para cargas de trabalho imprevisíveis ou novas aplicações.
    *   **Provisionado:** Pague por uma capacidade de leitura/escrita fixa. Mais barato para cargas de trabalho previsíveis e consistentes.

---

## 2. DynamoDB (NoSQL) vs. RDS (SQL)

A escolha não é sobre qual é "melhor", mas qual é a **ferramenta certa para o trabalho**. A decisão depende fundamentalmente do seu **padrão de acesso aos dados**.

| Característica | DynamoDB (NoSQL) | RDS (SQL - ex: PostgreSQL, MySQL) |
| :--- | :--- | :--- |
| **Estrutura** | Flexível (schemaless) - Itens em uma coleção. | Rígida (schema-on-write) - Tabelas com colunas definidas. |
| **Modelo de Dados** | Chave-Valor, Documento. | Relacional (tabelas conectadas por chaves estrangeiras). |
| **Escalabilidade** | **Horizontal** (adiciona mais servidores). Escala "infinita". | **Vertical** (aumenta a potência do servidor). Escala limitada. |
| **Performance** | Previsível e ultra-rápida para consultas por chave. | Depende da complexidade dos `JOINs`, índices e otimização. |
| **Consultas** | Otimizado para `GetItem`, `Query` e `Scan`. **Sem `JOINs`**. | Linguagem SQL completa (`JOINs`, agregações complexas, subqueries). |
| **Casos de Uso** | Apps de alta escala, IoT, jogos, perfis de usuário, catálogos. | Sistemas transacionais (ERP, CRM), Business Intelligence, relatórios. |
| **Mentalidade** | "Comece com as perguntas (queries) em mente." | "Comece com os dados (entidades) em mente." |

**Quando escolher DynamoDB?**
*   ✅ Seus padrões de consulta são **conhecidos e limitados**.
*   ✅ Você precisa de **latência extremamente baixa** e escalabilidade massiva.
*   ✅ Sua estrutura de dados é simples, evolui rapidamente ou varia muito entre os itens.

**Quando escolher RDS?**
*   ✅ Você precisa de **consultas ad-hoc complexas** e `JOINs` entre tabelas.
*   ✅ Sua aplicação requer conformidade **ACID** estrita para transações complexas.
*   ✅ Você não conhece todos os padrões de consulta antecipadamente.

---

## 3. Conceitos Fundamentais do DynamoDB

### 3.1. Tabelas, Itens e Atributos

*   **Tabela:** Um conjunto de itens. Pense nela como uma coleção de documentos JSON.
*   **Item:** Um único registro na tabela, similar a uma linha em SQL ou um documento em MongoDB.
*   **Atributo:** Um par de chave-valor em um item, como um campo ou coluna. Suporta tipos de dados como String, Number, Binary, Boolean, List e Map.

**Exemplo de Item (JSON):**
```json
{
    "id": "user-123",
    "nome": "Ana Silva",
    "idade": 34,
    "ativo": true,
    "enderecos": [
        {"tipo": "casa", "rua": "Rua A, 123"},
        {"tipo": "trabalho", "rua": "Av. B, 456"}
    ],
    "pedidos_recentes": {
        "pedido-001": "2024-10-25",
        "pedido-002": "2024-10-22"
    }
}
```

### 3.2. Chave Primária (Primary Key) - A Alma do DynamoDB

A chave primária é o que identifica unicamente cada item na tabela. **É a decisão de design mais importante que você fará.**

#### Opção 1: Chave de Partição Simples (Partition Key)

*   **O que é:** Uma única chave que identifica o item.
*   **Como funciona:** O DynamoDB usa um hash do valor da chave de partição para determinar em qual "partição" (servidor físico) o dado será armazenado. Para ler o item, você fornece a chave e o DynamoDB sabe exatamente onde buscar.
*   **Exemplo:** Em uma tabela de `Usuarios`, o `id` do usuário é uma ótima chave de partição.

```
Tabela: Usuarios
Chave de Partição: 'id' (String)

| id (PK)   | nome        | email              |
|-----------|-------------|--------------------|
| user-123  | Ana Silva   | ana@exemplo.com    |
| user-456  | Beto Costa  | beto@exemplo.com   |
```

#### Opção 2: Chave Composta (Partition Key + Sort Key)

*   **O que é:** Uma combinação de duas chaves: a **chave de partição** e a **chave de ordenação (sort key)**.
*   **Como funciona:** Itens com a **mesma chave de partição** são armazenados juntos, fisicamente próximos e ordenados pela chave de ordenação.
*   **Superpoder:** Isso permite usar a operação `query` para buscar múltiplos itens com a mesma chave de partição e aplicar condições na chave de ordenação (ex: `começa_com`, `entre`, `maior_que`).

**Exemplo:** Em uma tabela de `Pedidos`, o `cliente_id` é a chave de partição e a `data_pedido` é a chave de ordenação.

```
Tabela: Pedidos
Chave de Partição: 'cliente_id'
Chave de Ordenação: 'data_pedido'

| cliente_id (PK) | data_pedido (SK) | id_pedido   | total |
|-----------------|------------------|-------------|-------|
| user-123        | 2024-10-25T10:00 | pedido-001  | 150.50|
| user-123        | 2024-10-26T11:30 | pedido-003  | 75.00 |
| user-456        | 2024-10-26T09:00 | pedido-002  | 200.00|
```
Com este design, você pode fazer perguntas como: "Traga-me todos os pedidos do cliente `user-123` feitos depois de `2024-10-26`".

---

## 4. Operações com Python (Boto3)

Vamos configurar a conexão e ver as operações CRUD.

```python
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import json

# --- Configuração ---
# Usar o resource é mais alto nível e pythonico
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# Exemplo de tabela
tabela_produtos = dynamodb.Table('Produtos')

# --- Helper para converter floats ---
# DynamoDB não aceita floats nativamente, use a classe Decimal
def tratar_floats_para_decimal(obj):
    """Converte recursivamente floats em um objeto para Decimals."""
    if isinstance(obj, list):
        return [tratar_floats_para_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: tratar_floats_para_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, float):
        # Converte float para string e depois para Decimal para evitar problemas de precisão
        return Decimal(str(obj))
    return obj

# Alternativa mais simples usando o loads do JSON
# item_decimal = json.loads(json.dumps(produto_dict), parse_float=Decimal)
```

### 4.1. `put_item` (Criar ou Sobrescrever)

```python
def criar_produto(id_produto, nome, preco, categoria):
    """Cria um novo produto na tabela, mas somente se o ID não existir."""
    produto = {
        'id': id_produto,
        'nome': nome,
        'preco': preco, # float será convertido
        'categoria': categoria,
        'em_estoque': True
    }
    item_com_decimal = tratar_floats_para_decimal(produto)
    
    try:
        tabela_produtos.put_item(
            Item=item_com_decimal,
            # Expressão de condição: uma "guarda" para a operação.
            # Só executa se o atributo 'id' ainda não existir no item.
            ConditionExpression='attribute_not_exists(id)'
        )
        print(f"✅ Produto '{nome}' criado com sucesso.")
    except ClientError as e:
        # Erro comum quando a condição falha
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"⚠️ Produto com ID '{id_produto}' já existe.")
        else:
            # Para outros erros (ex: throttling), propague a exceção
            raise

# Uso:
criar_produto("prod-001", "Notebook Pro X", 1499.99, "Eletrônicos")
```

### 4.2. `get_item` (Ler um Item)

A operação mais rápida e barata do DynamoDB. Sempre usa a chave primária completa.

```python
def buscar_produto(id_produto):
    """Busca um produto pela sua chave primária."""
    try:
        response = tabela_produtos.get_item(
            Key={'id': id_produto}
        )
        item = response.get('Item')
        
        if item:
            # O Boto3 converte Decimal de volta para float automaticamente
            print(f"🔍 Produto encontrado: {item['nome']} - R$ {item['preco']}")
            return item
        else:
            print(f"❌ Produto com ID '{id_produto}' não encontrado.")
            return None
    except ClientError as e:
        print(f"🚨 Erro ao buscar produto: {e.response['Error']['Message']}")
        # Implementar retry logic aqui em um cenário real

# Uso:
produto = buscar_produto("prod-001")
```

### 4.3. `update_item` (Atualizar um Item)

Permite modificar atributos específicos de um item atomicamente sem reescrevê-lo por inteiro.

```python
def atualizar_estoque_produto(id_produto, novo_preco, em_estoque):
    """Atualiza o preço e o status de estoque de um produto."""
    try:
        response = tabela_produtos.update_item(
            Key={'id': id_produto},
            # Expressão de atualização: define as ações a serem tomadas
            UpdateExpression="set preco = :p, #est = :e",
            # Mapeia nomes de atributos que são palavras reservadas do DynamoDB (ex: 'status')
            ExpressionAttributeNames={
                '#est': 'em_estoque'
            },
            # Mapeia os valores para evitar injeção e problemas de tipo
            ExpressionAttributeValues={
                ':p': Decimal(str(novo_preco)),
                ':e': em_estoque
            },
            # Condição para a atualização (opcional)
            ConditionExpression='attribute_exists(id)',
            # Retorna os valores dos atributos atualizados
            ReturnValues="UPDATED_NEW"
        )
        print(f"✅ Atributos atualizados: {response['Attributes']}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"❌ Produto com ID '{id_produto}' não existe para ser atualizado.")
        else:
            print(f"🚨 Erro ao atualizar: {e.response['Error']['Message']}")

# Uso:
atualizar_estoque_produto("prod-001", 1399.00, False)
```

### 4.4. `delete_item` (Remover um Item)

```python
def deletar_produto(id_produto):
    """Remove um produto da tabela."""
    try:
        tabela_produtos.delete_item(
            Key={'id': id_produto},
            # Pode-se adicionar uma ConditionExpression aqui também
        )
        print(f"🗑️ Produto '{id_produto}' deletado com sucesso.")
    except ClientError as e:
        print(f"🚨 Erro ao deletar: {e.response['Error']['Message']}")

# Uso:
# deletar_produto("prod-001")
```

---

## 5. Consultas: `query` vs. `scan`

### 5.1. `query` (A Forma Correta de Buscar Dados)

*   **O que faz:** Busca itens com base na **chave de partição** e, opcionalmente, em condições na **chave de ordenação**.
*   **Performance:** Muito rápida e eficiente. É a forma preferencial de buscar múltiplos dados.
*   **Requisito:** Você **deve** fornecer o valor exato da chave de partição.

**Exemplo (usando a tabela `Pedidos`):**
```python
from boto3.dynamodb.conditions import Key

tabela_pedidos = dynamodb.Table('Pedidos')

def buscar_pedidos_recentes_cliente(cliente_id, data_inicio):
    """Busca pedidos de um cliente a partir de uma data."""
    response = tabela_pedidos.query(
        # KeyConditionExpression especifica a condição na chave primária
        # Aqui, buscamos todos os itens onde 'cliente_id' é igual a X
        # E 'data_pedido' é maior que Y
        KeyConditionExpression=Key('cliente_id').eq(cliente_id) & Key('data_pedido').gt(data_inicio)
    )
    return response['Items']

# Busca todos os pedidos do cliente 'user-123' feitos depois de '2024-10-25'
pedidos_recentes = buscar_pedidos_recentes_cliente('user-123', '2024-10-25T00:00:00')
```

### 5.2. `scan` (A Varredura Perigosa)

*   **O que faz:** Lê **todos os itens** da tabela, um por um, e depois (opcionalmente) filtra os resultados.
*   **Performance:** Lenta e cara (consome muitas unidades de leitura). **Deve ser evitada em produção a todo custo.**
*   **Uso:** Apenas para operações de migração, scripts administrativos ou em tabelas muito pequenas.

**Exemplo (NÃO FAÇA ISSO EM PRODUÇÃO):**
```python
from boto3.dynamodb.conditions import Attr

def buscar_produtos_em_promocao():
    """Encontra produtos com preço abaixo de um valor, varrendo a tabela inteira."""
    # FilterExpression é aplicada DEPOIS de ler todos os itens da tabela.
    # Você paga pela leitura de todos os itens, mesmo que poucos sejam retornados.
    response = tabela_produtos.scan(
        FilterExpression=Attr('preco').lt(Decimal('500'))
    )
    return response['Items']

# CUIDADO: Isso lê a tabela inteira! Se a tabela tiver 10GB, ele vai ler 10GB.
produtos_baratos = buscar_produtos_em_promocao()
```

| Operação | Performance | Custo | Quando Usar |
| :--- | :--- | :--- | :--- |
| `get_item` | 🚀 A mais rápida | 💰 Mais baixo | Para ler um único item pela sua chave completa. |
| `query` | ✅ Rápida | 👍 Baixo | Para buscar um conjunto de itens com a mesma chave de partição. |
| `scan` | 🐢 Lenta | 💸 Alto | **Apenas para operações administrativas ou em tabelas muito pequenas.** |

---

## 6. Índices Secundários (Secondary Indexes)

E se você precisar consultar seus dados por um atributo que não é a chave primária? **A resposta nunca é `scan`**. A resposta é criar um **Índice Secundário**.

Um índice é essencialmente uma "cópia" dos seus dados, organizada com uma chave primária diferente, otimizada para um padrão de acesso específico.

### 6.1. Índice Secundário Global (GSI - Global Secondary Index)

*   **O que é:** Uma "tabela fantasma" com uma chave primária (partição e/ou ordenação) diferente da tabela base.
*   **Características:**
    *   Pode ser criado a qualquer momento.
    *   Tem sua própria capacidade provisionada (custo separado).
    *   A atualização é assíncrona (consistência eventual), então pode haver um pequeno delay.

**Exemplo:** Na nossa `tabela_produtos`, queremos buscar todos os produtos de uma `categoria` e ordená-los por `preco`.

1.  **Crie um GSI** na tabela `Produtos`:
    *   **Nome do Índice:** `categoria-preco-index`
    *   **Chave de Partição do Índice:** `categoria`
    *   **Chave de Ordenação do Índice:** `preco`

2.  **Use `query` no índice:**
    ```python
    def buscar_por_categoria_ordenado_por_preco(categoria):
        response = tabela_produtos.query(
            # Especifica que a query será no GSI
            IndexName='categoria-preco-index',
            KeyConditionExpression=Key('categoria').eq(categoria)
        )
        return response['Items']

    # Agora podemos buscar por categoria de forma eficiente!
    eletronicos = buscar_por_categoria_ordenado_por_preco("Eletrônicos")
    ```

### 6.2. Índice Secundário Local (LSI - Local Secondary Index)

*   **O que é:** Um índice que compartilha a **mesma chave de partição** da tabela base, mas tem uma **chave de ordenação diferente**.
*   **Características:**
    *   **Deve ser criado junto com a tabela.** Não pode ser adicionado depois.
    *   Compartilha a capacidade da tabela (sem custo extra de provisionamento).
    *   Oferece consistência forte ou eventual.

**Exemplo:** Na tabela `Pedidos`, queremos buscar os pedidos de um cliente ordenados por `status` em vez de `data_pedido`.

1.  **Crie um LSI** na tabela `Pedidos` no momento da criação da tabela:
    *   **Chave de Partição:** `cliente_id` (a mesma da tabela)
    *   **Chave de Ordenação do Índice:** `status`

### GSI vs. LSI

| Característica | Índice Secundário Global (GSI) | Índice Secundário Local (LSI) |
| :--- | :--- | :--- |
| **Chave de Partição** | Pode ser qualquer atributo. | **Deve ser a mesma** da tabela base. |
| **Chave de Ordenação** | Pode ser qualquer atributo. | **Deve ser diferente** da chave de ordenação da tabela base. |
| **Criação** | A qualquer momento. | Apenas na criação da tabela. |
| **Custo** | Capacidade provisionada separada (paga a mais). | Compartilha a capacidade da tabela (sem custo extra). |
| **Consistência** | Apenas Eventual. | Forte ou Eventual. |
| **Limite de Tamanho** | Sem limite. | A coleção de itens por chave de partição não pode exceder 10 GB. |

---

## 7. Padrões de Design Avançados

### 7.1. Single-Table Design (Design de Tabela Única)

Em vez de ter múltiplas tabelas (`Usuarios`, `Pedidos`, `Produtos`), você modela todas as suas entidades em uma única tabela.

*   **Como?** Usando chaves primárias genéricas (ex: `PK`, `SK`) e prefixos para identificar os tipos de entidade.
    *   `PK: USER#user-123`, `SK: PROFILE#user-123` (dados do usuário)
    *   `PK: USER#user-123`, `SK: ORDER#2024-10-26T11:30` (um pedido do usuário)
    *   `PK: ORDER#pedido-003`, `SK: ORDER#pedido-003` (dados do pedido)
*   **Por quê?** Para buscar dados de diferentes entidades em uma única `query`, evitando múltiplas viagens de rede. Por exemplo, buscar um usuário e seus 5 pedidos mais recentes em uma única requisição. É o equivalente a um `JOIN` pré-calculado.

### 7.2. DynamoDB Streams

*   **O que é:** Um fluxo de eventos que captura todas as modificações (criação, atualização, exclusão) em uma tabela do DynamoDB, em ordem.
*   **Como funciona:** Quando um item é modificado, um registro do evento (o item antes e/ou depois da mudança) é adicionado ao stream em tempo real.
*   **Caso de Uso Comum:** Integrar com o **AWS Lambda**. Uma função Lambda pode ser acionada por eventos do stream para executar ações, como:
    *   Replicar dados para outro serviço (ex: OpenSearch para buscas full-text).
    *   Enviar notificações (ex: "Seu pedido foi enviado!").
    *   Agregar dados para análise (ex: calcular o total de vendas do dia).

**Arquitetura Clássica:**
`App -> Tabela DynamoDB -> DynamoDB Stream -> Função AWS Lambda -> Envia notificação por e-mail/SNS`

---

## 8. Melhores Práticas e Dicas Finais

1.  **Pense nos Padrões de Acesso Primeiro:** O design da sua tabela depende de como você vai consultá-la. Gaste 80% do seu tempo pensando nas queries.
2.  **Escolha a Chave de Partição com Sabedoria:** Use uma chave com **alta cardinalidade** (muitos valores únicos) para distribuir a carga uniformemente e evitar "hot partitions". Um `id` de usuário é bom; um `status` (ativo/inativo) é péssimo.
3.  **Use `query` em vez de `scan`:** Modele seus dados e crie GSIs para que todas as suas buscas em produção usem `query`.
4.  **Use TTL (Time To Live):** Configure um atributo TTL para que o DynamoDB exclua itens expirados (sessões, logs, dados temporários) automaticamente e de graça.
5.  **Otimize Custos:**
    *   Use o modo **On-Demand** para cargas de trabalho imprevisíveis ou em desenvolvimento.
    *   Use o modo **Provisionado** com auto-scaling para cargas de trabalho previsíveis e economizar.
    *   Monitore o consumo e ajuste a capacidade.
6.  **Tratamento de Erros:** Implemente lógica de **retry com exponential backoff** para lidar com exceções de `ProvisionedThroughputExceededException` (throttling). Os SDKs da AWS geralmente fazem isso automaticamente.
7.  **Paginação:** As operações `query` e `scan` retornam no máximo 1 MB de dados. Se houver mais resultados, a resposta incluirá um `LastEvaluatedKey`. Você deve passá-lo na próxima chamada no parâmetro `ExclusiveStartKey` para obter a próxima página de resultados.

## Conclusão

O DynamoDB é uma ferramenta incrivelmente poderosa para construir aplicações modernas, escaláveis e de alta performance. O segredo para o sucesso é abandonar a mentalidade relacional e abraçar o modelo de dados NoSQL, projetando suas tabelas em torno dos padrões de acesso da sua aplicação. Com um bom design, o DynamoDB pode oferecer uma performance consistente e escalabilidade quase infinita com o mínimo de gerenciamento.