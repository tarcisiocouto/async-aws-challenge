Como um assistente que **sempre responde em português do Brasil** (conforme sua instrução salva), estou formatando o conteúdo do seu "Desafio Backend AWS: Catálogo de Produtos Assíncrono (AsyncCatalog)" em Markdown, conforme solicitado.

Aqui está o desafio, bem estruturado:

---

# 🚀 Desafio Backend AWS: Catálogo de Produtos Assíncrono (AsyncCatalog)

## Visão Geral

O objetivo é construir um sistema de catálogo de produtos com **processamento assíncrono** usando serviços **AWS Serverless**. O sistema deve garantir que a criação de um produto seja processada em segundo plano via fila de mensagens (SQS), retornando uma resposta imediata ao cliente.

Este desafio foca na prática com **API Gateway, AWS Lambda, SQS, DynamoDB e S3.**

---

## 1. Arquitetura e Serviços AWS Envolvidos

| Serviço | Função no Projeto | Implementação da Lógica | Objetivo de Estudo |
| :--- | :--- | :--- | :--- |
| **API Gateway** | Endpoint público `POST /products`. | Configuração de Roteamento e Mapeamento de Resposta. | Simulação de resposta assíncrona (`202`). |
| **AWS Lambda** (Serviço) | `CreateProductProcessor` (Função Lambda). | Código Python (`boto3`): Publica evento no SQS. | Publicação de eventos e integração com o Gateway. |
| **AWS SQS** | Fila de Mensagens (`product-queue`). | Serviço de Fila (Zero código). | Desacoplamento de serviços. |
| **AWS Lambda** (Serviço) | `ProductSaverWorker` (Função Lambda). | Código Python (`boto3`): Consome SQS e salva no DynamoDB/S3. | Consumo de eventos e Worker assíncrono. |
| **Amazon DynamoDB** | Banco de Dados (`ProductTable`). | Tabela NoSQL (Zero código). | Armazenamento de dados não-relacional. |
| **AWS S3** | Armazenamento (`reports-bucket`). | Bucket de Armazenamento (Zero código). | Armazenamento de artefatos. |

---

## 2. Fases do Desafio (Requisitos Funcionais)

### Fase 1: Gateway e Envio Assíncrono (API Gateway + AWS Lambda 1 + SQS)

**Requisito:** Criar o fluxo de entrada que recebe a requisição HTTP e a envia imediatamente para o SQS.

| Tarefa | Detalhamento de Implementação na AWS | Checklist |
| :--- | :--- | :---: |
| **1.1. Configuração do SQS** | Crie uma fila SQS padrão chamada `product-queue`. | [ ] |
| **1.2. Criação do AWS Lambda 1** | Crie a função Lambda (`CreateProductProcessor`). O *runtime* deve ser Python. | [ ] |
| **1.3. Implementação da Lógica de Publicação** | O código Python no AWS Lambda 1 deve usar `boto3` para enviar o corpo da requisição para a fila `product-queue`. O Lambda deve ter a permissão `sqs:SendMessage`. | [ ] |
| **1.4. Configuração do API Gateway** | Crie **API REST** (`POST /products`). Integrar com o AWS Lambda 1. Mapear a resposta de sucesso do Lambda (`200`) para um status **`202 (Accepted)`** do API Gateway, garantindo que o cliente não espere. | [ ] |

---

### Fase 2: Processamento e Persistência (AWS Lambda 2 + DynamoDB)

**Requisito:** Criar o worker que consome a fila e persiste os dados do produto no DynamoDB.

| Tarefa | Detalhamento de Implementação na AWS | Checklist |
| :--- | :--- | :---: |
| **2.1. Configuração do DynamoDB** | Crie a tabela DynamoDB chamada `ProductTable`. Chave primária: `id` (string). | [ ] |
| **2.2. Criação do AWS Lambda 2** | Crie a função Lambda (`ProductSaverWorker`) em Python. O código deve usar `boto3` para interagir com o DynamoDB. | [ ] |
| **2.3. Conexão SQS -> Lambda** | Configure o SQS como *trigger* (gatilho) do AWS Lambda 2. O Lambda 2 deve ter permissão de `sqs:ReceiveMessage` e `dynamodb:PutItem`. | [ ] |
| **2.4. Lógica do Worker** | O código Python deve: 1) Ler a mensagem do evento SQS. 2) Gerar um UUID único para o `id` do produto. 3) Persistir os dados (`id`, `nome`, `preço`, etc.) na tabela `ProductTable`. | [ ] |

---

### Fase 3: Geração de Relatório (S3)

**Requisito:** O worker deve gerar um artefato (relatório) e armazená-lo no S3.

| Tarefa | Detalhamento de Implementação na AWS | Checklist |
| :--- | :--- | :---: |
| **3.1. Configuração do S3** | Crie um bucket S3 com nome único (ex: `async-catalog-reports-seu-sobrenome`). | [ ] |
| **3.2. Configuração de Permissões** | Adicionar permissão (`s3:PutObject`) na Role de IAM do Lambda 2 para que ele possa escrever no bucket S3. | [ ] |
| **3.3. Lógica de Upload** | O código Python do AWS Lambda 2 deve, após salvar no DynamoDB, gerar uma *string* de texto simples (simulando um relatório) e usar `boto3` para fazer o *upload* desse artefato para o bucket S3, usando o `id` do produto como chave do arquivo. | [ ] |

---

## 3. Desafio Adicional (Exploração de GET e RDS)

Para uma aplicação completa, é importante buscar os dados.

| Tarefa | Detalhamento de Implementação na AWS | Checklist |
| :--- | :--- | :---: |
| **A.1. Criação do AWS Lambda 3** | Crie a função Lambda (`GetProduct`) em Python. | [ ] |
| **A.2. Configuração do API Gateway** | Adicione o endpoint **`GET /products/{id}`**. O `{id}` deve ser configurado como um *path parameter*. | [ ] |
| **A.3. Lógica de Busca** | O código Python do Lambda 3 deve ler o ID do *event* e usar o `boto3` para buscar e retornar os dados do produto na tabela DynamoDB. | [ ] |

### Requisito Opcional (RDS):

Substitua o DynamoDB pelo **Amazon RDS (PostgreSQL ou MySQL)**. Configure o Lambda 2 e 3 para se conectar ao RDS dentro de uma **VPC privada**. Isso explora a configuração de rede e banco de dados relacional em ambientes Lambda.

---