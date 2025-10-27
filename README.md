# AsyncCatalog: Desafio Backend AWS

Este projeto é uma implementação do desafio "AsyncCatalog", que consiste em um sistema de catálogo de produtos com processamento assíncrono usando serviços AWS Serverless.

O desafio completo pode ser encontrado em [CHALLENGE.md](./CHALLENGE.md).

## Visão Geral

O objetivo é construir um sistema de catálogo de produtos onde a criação de um produto é processada em segundo plano, utilizando uma fila de mensagens (SQS), o que garante uma resposta imediata ao cliente.

## Arquitetura

A arquitetura do projeto é baseada em serviços serverless da AWS, focando em desacoplamento, escalabilidade e resiliência.

| Serviço | Função no Projeto |
| :--- | :--- |
| **API Gateway** | Endpoint público `POST /products` e `GET /products/{id}`. |
| **AWS Lambda** | Funções para processar a criação e busca de produtos. |
| **AWS SQS** | Fila de Mensagens (`product-queue`) para desacoplar os serviços. |
| **Amazon DynamoDB** | Banco de Dados NoSQL (`ProductTable`) para armazenar os produtos. |
| **AWS S3** | Armazenamento de relatórios (`reports-bucket`). |

### Detalhes da Arquitetura

1.  **Criação de Produto (Fluxo Assíncrono)**:
    *   O cliente envia uma requisição `POST` para o endpoint `/products` no **API Gateway**.
    *   O API Gateway aciona a função Lambda `CreateProductProcessor`.
    *   A função `CreateProductProcessor` valida a requisição e publica uma mensagem com os dados do produto na fila `product-queue` do **SQS**.
    *   O API Gateway retorna imediatamente uma resposta `202 (Accepted)` para o cliente, indicando que a requisição foi aceita para processamento.
    *   A função Lambda `ProductSaverWorker` é acionada por novas mensagens na fila do SQS.
    *   A `ProductSaverWorker` processa a mensagem, gera um ID único para o produto, salva os dados na tabela `ProductTable` do **DynamoDB** e gera um relatório que é salvo no **S3**.

2.  **Busca de Produto (Fluxo Síncrono)**:
    *   O cliente envia uma requisição `GET` para o endpoint `/products/{id}` no **API Gateway**.
    *   O API Gateway aciona a função Lambda `GetProduct`.
    *   A função `GetProduct` busca o produto na tabela `ProductTable` do **DynamoDB** usando o ID fornecido.
    *   O API Gateway retorna a resposta `200 (OK)` com os dados do produto para o cliente.

## Tecnologias Utilizadas

*   **Backend**: Python, Django, Django REST Framework
*   **AWS Services**: API Gateway, Lambda, SQS, DynamoDB, S3
*   **AWS SDK**: `boto3`

## Como Executar o Projeto

### Pré-requisitos

*   Python 3.8+
*   Conta na AWS com as permissões necessárias para criar os recursos descritos na arquitetura.
*   AWS CLI configurado com as credenciais de acesso.

### Instalação

1.  Clone o repositório:
    ```bash
    git clone https://github.com/tarcisiocouto/async-aws-challenge.git
    cd async-aws-challenge
    ```

2.  Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Configuração

1.  Configure as variáveis de ambiente necessárias para a conexão com a AWS. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

    ```
    AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
    AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
    AWS_REGION=<YOUR_AWS_REGION>
    AWS_SQS_QUEUE_URL=<YOUR_SQS_QUEUE_URL>
    ```

### Executando Localmente

Para executar o servidor de desenvolvimento do Django:

```bash
python manage.py runserver
```

### Deploy na AWS

O deploy das funções Lambda e a configuração dos outros serviços da AWS devem ser feitos seguindo as instruções do [CHALLENGE.md](./CHALLENGE.md).

## Estrutura do Projeto

```
.
├── app/                # Configurações do Django
├── challenge/          # Aplicação Django principal
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── selectors.py
│   ├── services.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── lambda/             # Código das funções Lambda
│   ├── CreateProductProcessor.py
│   ├── GetProduct.py
│   └── ProductSaverWorker.py
├── CHALLENGE.md        # Descrição do desafio
├── manage.py           # Script de gerenciamento do Django
└── requirements.txt    # Dependências do projeto
```
