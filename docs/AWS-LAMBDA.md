# AWS Lambda: Guia Definitivo de Computação Serverless e Arquiteturas Orientadas a Eventos

**Versão 2.0: Revisado, expandido com padrões de design, testes locais e melhores práticas de produção.**

---

## 0. TL;DR (Resumo Rápido)

*   **O que é?** Um serviço que executa seu código em resposta a eventos (uma requisição HTTP, um upload de arquivo, uma mensagem em uma fila). Você não gerencia servidores.
*   **Como funciona?** Você faz o upload de uma função (ex: `lambda_handler` em Python). A AWS a executa em um container temporário quando um evento acontece.
*   **Modelo de Custo:** Você paga **apenas** pelos milissegundos que seu código executa e pelo número de requisições. Se não há execuções, o custo é zero.
*   **Principais Vantagens:** Escalabilidade automática, zero gerenciamento de servidores, custo-benefício para cargas de trabalho variáveis.
*   **Principais Desvantagens:** Limite de 15 minutos de execução, "cold starts" (latência na primeira chamada), complexidade no gerenciamento de estado.
*   **Quando usar?** APIs, processamento de dados em tempo real (ex: redimensionar imagens), automação de tarefas na nuvem (ex: backups), backends para aplicações web e móveis.
*   **Regra de Ouro:** Funções Lambda devem ser **pequenas, focadas e sem estado (stateless)**. Elas fazem uma coisa e fazem bem, orquestradas por outros serviços da AWS.

---

## 1. O que é AWS Lambda?

AWS Lambda é um serviço de computação **serverless** e **orientado a eventos**. Ele permite executar código em resposta a gatilhos (triggers) sem a necessidade de provisionar ou gerenciar servidores. Você simplesmente faz o upload do seu código, e o Lambda cuida de toda a infraestrutura necessária para executá-lo, escalá-lo e garantir alta disponibilidade.

**Analogia do Mundo Real:**

*   **Servidor Tradicional (EC2):** Ter um carro. Você é responsável pela manutenção, seguro, combustível e estacionamento. Ele está sempre disponível para você, mas você paga por ele mesmo quando não está dirigindo.
*   **AWS Lambda:** Usar um serviço de transporte por aplicativo (Uber, 99). Você só chama quando precisa de uma carona. Um motorista (ambiente de execução) aparece, te leva ao seu destino (executa o código) e vai embora. Você paga apenas pela viagem que fez.

### Lambda vs. Servidores Tradicionais (EC2)

| Característica | AWS Lambda (Serverless) | Amazon EC2 (Servidor Virtual) |
| :--- | :--- | :--- |
| **Abstração** | Função (FaaS - Function as a Service) | Máquina Virtual (IaaS - Infrastructure as a Service) |
| **Gerenciamento** | Nenhum (AWS gerencia SO, runtime, escala) | Você gerencia o SO, patches, segurança, escala. |
| **Escalabilidade** | Automática e por requisição. | Manual ou via Auto Scaling Groups (mais lento). |
| **Modelo de Custo** | Pague por execução (ms) e nº de requisições. | Pague por hora/segundo, mesmo que ocioso. |
| **Estado** | **Stateless** (sem estado). Cada invocação é nova. | **Stateful** (com estado). Pode manter dados em memória/disco. |
| **Limite de Tempo** | Máximo de 15 minutos. | Ilimitado. |
| **Casos de Uso** | APIs, processamento de eventos, automação. | Aplicações monolíticas, bancos de dados, tarefas de longa duração. |

---

## 2. Anatomia de uma Função Lambda

Toda função Lambda em Python tem um ponto de entrada (handler) com uma assinatura padrão.

```python
import json

def lambda_handler(event, context):
    """
    Ponto de entrada para a execução da Lambda.

    :param event: (dict) Dados do evento que acionou a função.
    :param context: (object) Informações sobre a execução (runtime).
    :return: (dict) Um dicionário que o Lambda serializa para JSON como resposta.
    """
    # O evento contém os dados do gatilho
    print(f"Evento recebido: {json.dumps(event, indent=2)}")
    
    # O contexto contém metadados da execução
    print(f"Request ID: {context.aws_request_id}")
    print(f"Tempo restante (ms): {context.get_remaining_time_in_millis()}")
    
    # A resposta para invocações síncronas (ex: API Gateway)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Função executada com sucesso!',
            'input_event': event
        })
    }
```

### 2.1. O Parâmetro `event` (O Quê?)

O `event` é um dicionário que contém a carga de dados (payload) do gatilho. Sua estrutura é **totalmente dependente da origem do evento**.

*   **API Gateway (Proxy Lambda):** Contém detalhes de uma requisição HTTP (`httpMethod`, `path`, `body`, `headers`, `queryStringParameters`).
*   **SQS:** Contém uma lista de `Records`, onde cada registro é uma mensagem da fila com um `body`.
*   **S3:** Contém uma lista de `Records` descrevendo o evento do S3 (ex: `eventName: "ObjectCreated:Put"`) e detalhes do objeto (`bucket`, `key`).
*   **EventBridge:** Contém o evento customizado que você definiu, com campos como `source`, `detail-type` e `detail` (seu payload).

**Sempre verifique a documentação do serviço de origem para saber a estrutura exata do evento!**

### 2.2. O Parâmetro `context` (Onde?)

O `context` é um objeto que fornece metadados sobre a invocação, a função e o ambiente de execução.

| Atributo | Descrição |
| :--- | :--- |
| `function_name` | O nome da sua função Lambda. |
| `aws_request_id` | O ID único da requisição. **Crucial para rastreabilidade e debugging.** |
| `invoked_function_arn` | O ARN (Amazon Resource Name) da função. |
| `memory_limit_in_mb` | A memória alocada para a função. |
| `get_remaining_time_in_millis()` | Função que retorna o tempo restante antes do timeout. Útil para operações longas. |
| `log_group_name` / `log_stream_name` | Onde os logs desta execução são armazenados no CloudWatch. |

---

## 3. Exemplo Prático: API com Validação e Dependências

Vamos evoluir o exemplo de cadastro de usuários, adicionando **validação de dados com Pydantic**, uma prática essencial em produção.

**Arquitetura:**
`Cliente -> API Gateway -> Lambda (com Pydantic) -> DynamoDB & SQS`

### 3.1. Empacotando Dependências

Lambda não vem com bibliotecas como `pydantic` ou `requests` pré-instaladas. Você precisa empacotá-las com seu código.

**Passo a passo para criar um pacote de deploy (.zip):**

1.  Crie uma pasta para o projeto: `mkdir meu-projeto && cd meu-projeto`
2.  Salve seu código Lambda em um arquivo, ex: `app.py`.
3.  Instale as dependências **dentro da pasta do projeto**:
    ```bash
    pip install pydantic -t .
    ```
    O `-t .` instrui o pip a instalar os pacotes no diretório atual.
4.  Sua pasta agora se parece com:
    ```
    meu-projeto/
    ├── app.py
    ├── pydantic/
    ├── pydantic_core/
    └── ... (outras dependências)
    ```
5.  Crie o arquivo ZIP a partir do **conteúdo** da pasta:
    ```bash
    zip -r ../deployment-package.zip .
    ```

Este `deployment-package.zip` é o arquivo que você fará upload para o Lambda.

> **Melhor Alternativa:** Para projetos maiores, use **Lambda Layers** para gerenciar dependências compartilhadas, reduzindo o tamanho do seu pacote de deploy.

### 3.2. Código da Função com Pydantic (`app.py`)

```python
import json
import boto3
import os
import logging
from datetime import datetime
from pydantic import BaseModel, EmailStr, ValidationError

# --- Configuração ---
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

TABLE_NAME = os.environ['USERS_TABLE']
QUEUE_URL = os.environ['WELCOME_EMAIL_QUEUE_URL']

# --- Modelo de Validação com Pydantic ---
class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr # Validação de e-mail gratuita!

# --- Handler Principal ---
def lambda_handler(event, context):
    logger.info(f"Iniciando execução {context.aws_request_id}")
    
    try:
        # 1. Validar o corpo da requisição
        body = json.loads(event.get('body', '{}'))
        user_data = CreateUserRequest(**body)

    except json.JSONDecodeError:
        logger.warning("Corpo da requisição não é um JSON válido.")
        return create_response(400, {'error': 'JSON mal formatado.'})
    except ValidationError as e:
        logger.warning(f"Falha na validação dos dados: {e.errors()}")
        return create_response(400, {'error': 'Dados de entrada inválidos', 'details': e.errors()})

    try:
        # 2. Processar a lógica de negócio
        user_id = f"user_{int(datetime.now().timestamp() * 1000)}"
        
        # 3. Salvar no DynamoDB
        save_user_to_dynamo(user_id, user_data)
        logger.info(f"Usuário {user_id} ({user_data.email}) salvo no DynamoDB.")

        # 4. Enviar para o SQS
        send_welcome_message_to_sqs(user_id, user_data)
        logger.info(f"Mensagem para o usuário {user_id} enviada para a fila SQS.")

        # 5. Retornar sucesso
        return create_response(201, {'message': 'Usuário criado com sucesso!', 'userId': user_id})

    except Exception as e:
        logger.exception("Erro inesperado ao processar a requisição.")
        return create_response(500, {'error': 'Erro interno do servidor.'})

# --- Funções Auxiliares (boa prática) ---
def save_user_to_dynamo(user_id, user_data):
    table = dynamodb.Table(TABLE_NAME)
    timestamp = datetime.utcnow().isoformat()
    table.put_item(Item={
        'id': user_id,
        'email': user_data.email,
        'name': user_data.name,
        'createdAt': timestamp,
    })

def send_welcome_message_to_sqs(user_id, user_data):
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            'userId': user_id,
            'email': user_data.email,
            'name': user_data.name
        })
    )

def create_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
```

---

## 4. Testando Localmente com AWS SAM

Desenvolver e testar fazendo deploy na nuvem é lento. Use o **AWS Serverless Application Model (SAM)** para testar localmente.

1.  **Instale o SAM CLI:** Siga as instruções no site da AWS.
2.  **Crie um template SAM (`template.yaml`):** Este arquivo descreve sua infraestrutura serverless.
    ```yaml
    AWSTemplateFormatVersion: '2010-09-09'
    Transform: AWS::Serverless-2016-10-31
    Resources:
      MyApiFunction:
        Type: AWS::Serverless::Function
        Properties:
          CodeUri: meu-projeto/ # Pasta com o código e dependências
          Handler: app.lambda_handler
          Runtime: python3.9
          Events:
            CreateUser:
              Type: Api
              Properties:
                Path: /users
                Method: post
    ```
3.  **Invoque a função localmente:**
    ```bash
    # Crie um arquivo com o evento de teste (ex: event.json)
    echo '{"body": "{\"name\": \"Tarcísio\", \"email\": \"tarcisio@example.com\"}"}' > event.json

    # Invoque a função
    sam local invoke MyApiFunction -e event.json
    ```
4.  **Inicie uma API local:**
    ```bash
    sam local start-api
    ```
    Agora você pode fazer requisições `POST` para `http://127.0.0.1:3000/users` e testar sua API em tempo real.

---

## 5. Tópicos Avançados de Produção

### 5.1. Cold Starts

*   **O que é:** A latência da primeira invocação após um período de inatividade. O Lambda precisa criar um novo ambiente de execução: baixar o código, iniciar o runtime e executar o código de inicialização (fora do handler).
*   **Impacto:** Adiciona latência (de ~100ms a vários segundos) à primeira requisição.
*   **Como Mitigar:**
    *   **Provisioned Concurrency:** Pague para manter um número de ambientes "quentes" e prontos, eliminando cold starts (tem custo).
    *   **Otimize o Pacote:** Mantenha o tamanho do seu código e dependências o menor possível.
    *   **Código de Inicialização Leve:** Inicialize clientes e conexões fora do handler, mas evite operações pesadas.
    *   **Evite VPCs se não for necessário:** Lambdas em VPCs historicamente têm cold starts mais longos.

### 5.2. Concorrência e Throttling

*   **Concurrency (Concorrência):** O número de execuções simultâneas da sua função. Por padrão, sua conta tem um limite regional (ex: 1000 execuções simultâneas) compartilhado entre todas as funções.
*   **Throttling:** O que acontece quando as requisições chegam mais rápido do que a capacidade de escalar ou o limite de concorrência. O Lambda rejeitará as invocações (erro `429 Too Many Requests`).
*   **Reserved Concurrency:** Garante um número máximo de execuções para uma função específica, protegendo-a de outras funções "barulhentas".

### 5.3. Tratamento de Erros e DLQ

*   **Invocações Síncronas (API Gateway):** O erro é retornado ao cliente. O Lambda **não** tenta novamente.
*   **Invocações Assíncronas (S3, EventBridge):** O Lambda tenta novamente **2 vezes** por padrão. Se todas falharem, o evento é descartado.
*   **Gatilhos de Streams (SQS, DynamoDB Streams):** O lote de mensagens retorna à fila/stream e é reprocessado até ter sucesso ou expirar. Isso pode levar a um loop infinito de falhas.
*   **Dead-Letter Queue (DLQ):** **Essencial para sistemas assíncronos e de streams.** Configure uma fila SQS ou tópico SNS como DLQ. Se uma função falhar após todas as retentativas, o evento com falha é enviado para a DLQ para análise posterior, evitando a perda de dados.

---

## 6. Melhores Práticas Essenciais

1.  **Princípio do Menor Privilégio:** A IAM Role da sua função deve ter **apenas** as permissões necessárias (ex: `dynamodb:PutItem` na tabela X, e nada mais).
2.  **Use Variáveis de Ambiente e Secrets Manager:** Nunca hardcode segredos ou configurações. Use variáveis de ambiente para configurações não sensíveis e **AWS Secrets Manager** ou **Parameter Store** para credenciais de banco de dados, chaves de API, etc.
3.  **Implemente Logging Estruturado:** Use `logger.info({"action": "create_user", "user_id": user_id})`. Logs em JSON são pesquisáveis e analisáveis no CloudWatch Logs Insights.
4.  **Seja Idempotente:** Especialmente com gatilhos assíncronos, sua função pode receber o mesmo evento mais de uma vez. Garanta que processar o mesmo evento múltiplas vezes não cause efeitos colaterais indesejados (ex: não crie o mesmo usuário duas vezes).
5.  **Monitore Tudo:** Crie alarmes no CloudWatch para métricas chave: `Errors` (taxa de erro > 1%), `Throttles` e `Duration` (próximo do timeout). Use o **AWS X-Ray** para rastrear requisições em sistemas distribuídos.

## Conclusão

O AWS Lambda é mais do que apenas "código sem servidor"; é o pilar de arquiteturas modernas, resilientes e escaláveis na nuvem. Dominar o Lambda significa entender o fluxo de eventos, o gerenciamento de dependências, a segurança e a observabilidade. Ao adotar as práticas corretas, você pode construir sistemas complexos que escalam massivamente com custo otimizado e baixo esforço operacional.