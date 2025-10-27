# Tutorial AWS: Construindo uma Aplicação Serverless Completa com AWS SAM

**Versão 2.0: Um guia prático e completo, do zero ao deploy.**

---

## 1. Introdução ao Projeto

Bem-vindo a este guia prático para construir uma aplicação serverless real na AWS. Em vez de apenas ler sobre os serviços, vamos usá-los em conjunto para criar uma solução robusta, escalável e orientada a eventos. Usaremos o **AWS Serverless Application Model (SAM)**, o framework padrão da AWS para construir e implantar aplicações serverless.

**O Projeto: Um Serviço de Processamento de Imagens Assíncrono**

Vamos construir um sistema onde um usuário pode enviar uma imagem, e a aplicação irá automaticamente gerar uma thumbnail (miniatura), salvar metadados em um banco de dados e enfileirar uma notificação. Tudo de forma assíncrona, garantindo uma experiência de usuário rápida e um sistema resiliente.

### Arquitetura da Solução (O que vamos construir)

```
+-----------+  1. Upload  +---------------------+  2. Event   +------------------------+
|  Usuário  | ----------> | Bucket S3 (Uploads) | ----------> |  Lambda (Processador)  |
+-----------+             +---------------------+             +------------------------+
                                                                  |         |         |
                                                                  | 3.      | 4.      | 5.
                                                       (Salva     | (Salva  | (Envia  |
                                                       Thumbnail) | Metadados) | Mensagem)
                                                                  |         |         |
                                                                  v         v         v
                                                      +-----------+ +---------+ +-----------+
                                                      | Bucket S3 | |DynamoDB | | Fila SQS  |
                                                      |(Thumbnails)| | (Tabela)| |(Notificações)|
                                                      +-----------+ +---------+ +-----------+
                                                                                    |
                                                                                    | 6. Event
                                                                                    v
                                                                          +------------------+
                                                                          | Lambda (Notificador) |
                                                                          +------------------+
```

---

## 2. Pré-requisitos e Configuração Inicial

Antes de começar, garanta que você tenha o seguinte ambiente configurado.

1.  **Conta AWS:** Se não tiver, crie uma no [site da AWS](https://aws.amazon.com/free/).
2.  **AWS CLI:** Instale e configure a AWS Command Line Interface.
    ```bash
    aws configure
    # AWS Access Key ID [...]: SEU_ACCESS_KEY
    # AWS Secret Access Key [...]: SEU_SECRET_KEY
    # Default region name [...]: us-east-1  (ou sua região de preferência)
    # Default output format [...]: json
    ```
3.  **Python 3.9+** e **Pip**.
4.  **AWS SAM CLI:** Siga o [guia de instalação oficial](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).
5.  **Docker:** É necessário para o SAM testar as funções Lambda localmente. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### Iniciando o Projeto com SAM

O SAM CLI irá criar toda a estrutura de pastas e arquivos para nós.

```bash
# Crie um projeto SAM "Hello World". Nós vamos modificá-lo.
sam init

# Responda às perguntas:
# Which template source would you like to use? -> 1 - AWS Quick Start Templates
# Choose an AWS Quick Start application template -> 1 - Hello World Example
# Use the most popular runtime and package type? (Python and zip) [y/N] -> y
# Would you like to enable X-Ray tracing for the function(s) in your application? [y/N] -> N
# Project name [sam-app]: -> serverless-image-processor

# Entre na pasta do projeto
cd serverless-image-processor
```

Agora você tem uma pasta `serverless-image-processor` com um `template.yaml` e uma pasta `hello_world`. Vamos modificar esses arquivos para criar nossa aplicação.

---

## 3. Módulo 1: Definindo a Infraestrutura com SAM (`template.yaml`)

O arquivo `template.yaml` é o coração do nosso projeto. Ele descreve todos os recursos da AWS que precisamos. **Substitua todo o conteúdo do seu `template.yaml` por este código:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  Uma aplicação serverless para processar imagens com S3, Lambda, DynamoDB e SQS.

Globals:
  Function:
    Timeout: 30
    MemorySize: 256

Resources:
  # --- 1. Buckets S3 ---
  UploadsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-uploads-bucket"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  ThumbnailsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "${AWS::StackName}-thumbnails-bucket"
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # --- 2. Tabela DynamoDB ---
  ImageMetadataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-ImageMetadata"
      AttributeDefinitions:
        - AttributeName: "ImageID"
          AttributeType: "S"
      KeySchema:
        - AttributeName: "ImageID"
          KeyType: "HASH"
      BillingMode: PAY_PER_REQUEST

  # --- 3. Fila SQS e Dead-Letter Queue ---
  NotificationsDLQ:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-Notifications-DLQ"

  NotificationsQueue:
    Type: AWS::SQS::Queue
    Properties:
      QueueName: !Sub "${AWS::StackName}-Notifications-Queue"
      RedrivePolicy:
        deadLetterTargetArn: !GetAtt NotificationsDLQ.Arn
        maxReceiveCount: 3

  # --- 4. Função Lambda Principal (Processador de Imagem) ---
  ImageProcessorFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/image_processor/
      Handler: app.lambda_handler
      Runtime: python3.9
      Architectures:
        - x86_64
      Policies:
        - S3ReadPolicy:
            BucketName: !Ref UploadsBucket
        - S3WritePolicy:
            BucketName: !Ref ThumbnailsBucket
        - DynamoDBCrudPolicy:
            TableName: !Ref ImageMetadataTable
        - SQSSendMessagePolicy:
            QueueName: !GetAtt NotificationsQueue.QueueName
      Environment:
        Variables:
          THUMBNAILS_BUCKET_NAME: !Ref ThumbnailsBucket
          DYNAMODB_TABLE_NAME: !Ref ImageMetadataTable
          SQS_QUEUE_URL: !Ref NotificationsQueue
      Events:
        S3UploadEvent:
          Type: S3
          Properties:
            Bucket: !Ref UploadsBucket
            Events: s3:ObjectCreated:*

  # --- 5. Função Lambda Secundária (Notificador) ---
  NotificationFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/notification_service/
      Handler: app.lambda_handler
      Runtime: python3.9
      Architectures:
        - x86_64
      Events:
        SQSNotificationEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt NotificationsQueue.Arn
            BatchSize: 10

Outputs:
  UploadsBucketName:
    Description: "Nome do bucket S3 para fazer upload de imagens."
    Value: !Ref UploadsBucket
```

---

## 4. Módulo 2: Escrevendo o Código das Funções Lambda

Agora, vamos criar o código Python para nossas duas funções.

1.  Delete a pasta `hello_world` que o `sam init` criou.
2.  Crie uma nova pasta `src`.
3.  Dentro de `src`, crie duas pastas: `image_processor` and `notification_service`.

### 4.1. O Processador de Imagens (`src/image_processor/app.py`)

Esta função é o coração do sistema. Ela precisa da biblioteca `Pillow` para manipular imagens.

**Crie o arquivo `src/image_processor/requirements.txt`:**
```txt
Pillow
```

**Agora, crie o arquivo `src/image_processor/app.py` e adicione o seguinte código:**

```python
import boto3
import os
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import json

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sqs_client = boto3.client('sqs')

THUMBNAILS_BUCKET_NAME = os.environ['THUMBNAILS_BUCKET_NAME']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    print("Evento recebido:", json.dumps(event))
    
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    
    for record in event['Records']:
        # 1. Obter informações do evento S3
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        download_path = f'/tmp/{uuid.uuid4()}-{os.path.basename(key)}'
        upload_path = f'/tmp/thumbnail-{os.path.basename(key)}'
        
        print(f"Processando s3://{bucket}/{key}")

        try:
            # 2. Baixar a imagem do S3
            s3_client.download_file(bucket, key, download_path)

            # 3. Criar a thumbnail com Pillow
            with Image.open(download_path) as image:
                image.thumbnail((128, 128))
                image.save(upload_path)

            # 4. Fazer upload da thumbnail para o outro bucket
            thumbnail_key = f"thumb-{key}"
            s3_client.upload_file(upload_path, THUMBNAILS_BUCKET_NAME, thumbnail_key)
            print(f"Thumbnail salva em s3://{THUMBNAILS_BUCKET_NAME}/{thumbnail_key}")

            # 5. Salvar metadados no DynamoDB
            image_id = str(uuid.uuid4())
            table.put_item(
                Item={
                    'ImageID': image_id,
                    'OriginalKey': key,
                    'ThumbnailKey': thumbnail_key,
                    'Status': 'PROCESSED'
                }
            )
            print(f"Metadados salvos no DynamoDB com ImageID: {image_id}")

            # 6. Enviar mensagem para o SQS
            sqs_client.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps({
                    'ImageID': image_id,
                    'Status': 'PROCESSED',
                    'Message': 'Imagem processada com sucesso.'
                })
            )
            print("Mensagem enviada para a fila SQS.")

        except Exception as e:
            print(f"Erro ao processar a imagem {key}: {e}")
            # (Opcional) Salvar status de erro no DynamoDB ou enviar para outra fila
            raise e

    return {'statusCode': 200, 'body': json.dumps('Processamento concluído')}
```

### 4.2. O Serviço de Notificação (`src/notification_service/app.py`)

Esta função é muito mais simples. Ela é acionada por mensagens na fila SQS.

**Crie o arquivo `src/notification_service/app.py`:**

```python
import json

def lambda_handler(event, context):
    print("Evento recebido:", json.dumps(event))
    
    for record in event['Records']:
        try:
            message_body = json.loads(record['body'])
            print("--- Nova Notificação ---")
            print(f"Status: {message_body.get('Status')}")
            print(f"ImageID: {message_body.get('ImageID')}")
            print(f"Mensagem: {message_body.get('Message')}")
            print("Simulando envio de e-mail ou notificação push...")
            print("----------------------")
        except Exception as e:
            print(f"Erro ao processar mensagem SQS: {e}")
            # A falha fará com que a mensagem retorne à fila para nova tentativa
            raise e
            
    return {'statusCode': 200, 'body': json.dumps('Notificações processadas')}
```

---

## 5. Módulo 3: Build, Deploy e Teste

Agora que a infraestrutura e o código estão prontos, vamos implantar na AWS.

### 5.1. Build

O comando `sam build` irá baixar as dependências (Pillow), organizá-las e preparar tudo para o deploy.

```bash
sam build
```

### 5.2. Deploy

O comando `sam deploy` envia sua aplicação para a AWS CloudFormation, que provisionará todos os recursos definidos no `template.yaml`.

```bash
sam deploy --guided
```

Responda às perguntas. Você pode usar os valores padrão para a maioria delas.
*   **Stack Name:** `serverless-image-processor`
*   **AWS Region:** `us-east-1` (ou a sua região)
*   **Confirm changes before deploy:** `y`
*   **Allow SAM CLI IAM role creation:** `y`
*   **Save arguments to samconfig.toml:** `y`

O SAM irá mostrar os recursos que serão criados. Revise e confirme com `y`.

O deploy pode levar alguns minutos. Ao final, ele mostrará o nome do seu bucket de uploads na seção `Outputs`.

### 5.3. Teste

1.  **Encontre o nome do seu bucket de upload.** Você pode pegá-lo na saída do `sam deploy` ou executar:
    ```bash
    aws cloudformation describe-stacks --stack-name serverless-image-processor --query "Stacks[0].Outputs[?OutputKey=='UploadsBucketName'].OutputValue" --output text
    ```

2.  **Faça o upload de um arquivo de imagem para o bucket.** (Substitua `SEU-BUCKET-AQUI` pelo nome do seu bucket).
    ```bash
    # Crie um arquivo de imagem de teste ou use um que você já tenha
    aws s3 cp ./sua-imagem.jpg s3://SEU-BUCKET-AQUI/
    ```

3.  **Verifique os resultados!**
    *   **Logs da Lambda:** Verifique os logs em tempo real para ver a execução.
        ```bash
        sam logs --stack-name serverless-image-processor --name ImageProcessorFunction --tail
        sam logs --stack-name serverless-image-processor --name NotificationFunction --tail
        ```
    *   **Bucket de Thumbnails:** Verifique se a thumbnail foi criada.
    *   **Tabela DynamoDB:** Verifique se os metadados foram salvos.
    *   **Fila SQS:** Verifique se a mensagem foi enviada e processada.

---

## 6. Limpeza

Para evitar custos contínuos, é **muito importante** deletar todos os recursos que você criou quando terminar de explorar o projeto.

**Atenção:** Este comando irá deletar **TUDO** que foi criado, incluindo os buckets S3 e os dados dentro deles.

```bash
sam delete
```

Confirme com `y` e o AWS SAM/CloudFormation irá remover toda a stack.

## Conclusão

Parabéns! Você construiu e implantou uma aplicação serverless completa e robusta na AWS. Você aprendeu na prática como S3, Lambda, DynamoDB e SQS se conectam para formar arquiteturas orientadas a eventos. A partir daqui, você pode explorar os "Próximos Passos" do documento original, como adicionar um API Gateway para visualizar os dados ou o Cognito para autenticação.