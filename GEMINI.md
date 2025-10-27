# Project Overview

This project is a Django application that implements an asynchronous product catalog using AWS services. The goal is to receive product information via a REST API, process it asynchronously using a message queue (SQS), and store it in a database (DynamoDB). The project is based on the "AsyncCatalog" challenge described in `CHALLENGE.md`.

**Key Technologies:**

*   **Backend:** Python, Django, Django REST Framework
*   **AWS Services:** API Gateway, Lambda, SQS, DynamoDB, S3
*   **AWS SDK:** `boto3`

**Architecture:**

1.  A `POST` request with product data is sent to a Django REST Framework endpoint.
2.  The Django view calls a service that triggers an AWS Lambda function (`CreateProductProcessor`).
3.  The `CreateProductProcessor` Lambda function sends a message containing the product data to an SQS queue (`product-queue`).
4.  A second Lambda function (`ProductSaverWorker`) is triggered by messages in the SQS queue.
5.  The `ProductSaverWorker` function processes the message, generates a unique ID for the product, and saves the product data to a DynamoDB table (`ProductTable`).
6.  The `ProductSaverWorker` also generates a report and uploads it to an S3 bucket.

# Building and Running

**1. Install Dependencies:**

```bash
pip install -r requirements.txt
```

**2. Configure Environment Variables:**

Create a `.env` file in the project root and add the necessary AWS credentials and other configuration:

```
AWS_ACCESS_KEY_ID=<YOUR_AWS_ACCESS_KEY_ID>
AWS_SECRET_ACCESS_KEY=<YOUR_AWS_SECRET_ACCESS_KEY>
AWS_REGION=<YOUR_AWS_REGION>
AWS_SQS_QUEUE_URL=<YOUR_SQS_QUEUE_URL>
```

**3. Run the Django Development Server:**

```bash
python manage.py runserver
```

**4. Deploying Lambda Functions:**

The Lambda functions in the `lambda/` directory need to be deployed to AWS. The `CHALLENGE.md` file provides instructions on how to set up the necessary AWS resources.

# Development Conventions

*   The main application logic is in the `challenge` Django app.
*   The `CHALLENGE.md` file is the primary source of requirements and architecture for this project.
*   Use `boto3` to interact with AWS services.
*   Environment variables are used for configuration. See `app/settings.py` and `lambda/CreateProductProcessor.py`.
*   The `Product` model is defined in `challenge/models.py`.
*   The API endpoint is defined in `challenge/views.py` and `challenge/urls.py`.

# commits.md

### O Básico do Conventional Commits

Este padrão propõe uma estrutura de commit simples e obrigatória:

`<tipo>[escopo opcional]: <descrição>`

**1. `<tipo>` (Obrigatório)**

É uma palavra que descreve o tipo de alteração. Isso ajuda a categorizar a mudança e permite que ferramentas automatizadas gerem changelogs.

| Tipo | Descrição |
| --- | --- |
| `feat` | Uma nova funcionalidade. |
| `fix` | Uma correção de bug. |
| `docs` | Alterações na documentação. |
| `style` | Alterações de formatação (espaços, ponto e vírgula, etc.). |
| `refactor` | Uma alteração de código que não corrige um bug nem adiciona uma funcionalidade. |
| `test` | Adição de testes ou correção de testes existentes. |
| `chore` | Alterações em ferramentas de build ou outras tarefas que não afetam o código-fonte (ex: `.gitignore`, dependências). |

**2. `[escopo opcional]`**

Fornece um contexto mais detalhado sobre a alteração. É uma palavra ou frase curta, geralmente entre parênteses, que identifica a parte do código ou módulo afetado.

- `feat(auth)`: Adicionada funcionalidade de login.
- `fix(api)`: Corrigido bug de autenticação na API.
- `refactor(database)`: Refatorado o esquema do banco de dados.

**3. `<descrição>` (Obrigatório)**

Uma descrição curta e clara da alteração, escrita no imperativo (`"Adicionar funcionalidade"`, não `"Adicionei funcionalidade"`).

---

### Colocando em Prática

Vamos ver alguns exemplos de commits bons e ruins.

**❌ Comits ruins (sem padrão)**

- `Corrigido bug` (não diz qual bug nem onde)
- `Atualizado o código` (muito genérico)
- `reajuste no index` (falta de contexto, difícil de pesquisar)

**✅ Commits bons (seguindo o padrão)**

- `feat(users): adicionar campo de data de nascimento`
- `fix(api): corrigir erro 500 ao listar produtos sem imagem`
- `docs: atualizar README com informações de instalação`
- `refactor(views): separar lógica de negócios em services`

### Dicas Extras

- **Corpo do Commit**: Para mudanças mais complexas, adicione uma linha em branco após a descrição e escreva um parágrafo detalhado explicando o **motivo** da alteração, os **impactos** e as **decisões** tomadas.
- **Quebras de Linha (`BREAKING CHANGE`)**: Se sua alteração quebra a compatibilidade com versões anteriores, use a palavra-chave `BREAKING CHANGE:` no corpo do commit para destacar isso.

Adotar esse padrão de commit vai transformar seu histórico do Git de uma bagunça de mensagens sem sentido em um registro claro e pesquisável, facilitando a manutenção e a colaboração no projeto.