# AWS Lambda: Computação Serverless

## Visão Geral

AWS Lambda é um serviço de computação serverless que permite executar código sem provisionar ou gerenciar servidores. Suporta múltiplas linguagens e integra-se facilmente com outros serviços AWS.

## Características Principais

- Execução sob demanda
- Escalabilidade automática
- Cobrança por tempo de execução
- Suporte a várias linguagens (Python, Node.js, Java, etc.)

## Casos de Uso

1. Processamento de dados
2. Backends de API
3. Automação de infraestrutura
4. Processamento de eventos em tempo real
5. Machine Learning

## Exemplo de Código Lambda em Python

```python
import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Função Lambda para processamento de pedidos
    Integração com DynamoDB e tratamento de erros
    """
    try:
        # Validação de entrada
        if not event or 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Dados inválidos'})
            }
        
        # Parse do corpo da requisição
        pedido = json.loads(event['body'])
        
        # Validações de negócio
        if not pedido.get('cliente') or not pedido.get('valor'):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Dados obrigatórios ausentes'})
            }
        
        # Conectar ao DynamoDB
        dynamodb = boto3.resource('dynamodb')
        tabela = dynamodb.Table(os.environ['TABELA_PEDIDOS'])
        
        # Salvar pedido
        tabela.put_item(Item={
            'id_pedido': pedido['id'],
            'cliente': pedido['cliente'],
            'valor': pedido['valor']
        })
        
        # Enviar notificação por SNS (opcional)
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['TOPIC_NOTIFICACOES'],
            Message=json.dumps({
                'mensagem': 'Novo pedido processado',
                'id_pedido': pedido['id']
            })
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'mensagem': 'Pedido processado com sucesso',
                'id_pedido': pedido['id']
            })
        }
    
    except ClientError as e:
        # Tratamento de erros específicos do AWS SDK
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Erro no processamento',
                'detalhes': str(e)
            })
        }
    
    except Exception as e:
        # Tratamento de erros genéricos
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Erro interno do servidor',
                'detalhes': str(e)
            })
        }

# Configurações para teste local
def main():
    evento_teste = {
        'body': json.dumps({
            'id': '123456',
            'cliente': 'João Silva',
            'valor': 250.75
        })
    }
    resultado = lambda_handler(evento_teste, None)
    print(resultado)

if __name__ == '__main__':
    main()
```

## Melhores Práticas

1. **Otimização de Performance**
   - Minimizar tamanho do pacote de implantação
   - Usar AWS Lambda Layers
   - Configurar memória e timeout adequadamente

2. **Segurança**
   - Usar funções IAM com princípio de menor privilégio
   - Habilitar AWS X-Ray para rastreamento
   - Criptografar variáveis de ambiente sensíveis

3. **Monitoramento**
   - CloudWatch Logs
   - CloudWatch Metrics
   - AWS X-Ray

## Estratégias de Configuração

### Cold Start
- Manter funções pequenas e rápidas
- Usar provisioned concurrency
- Linguagens mais leves (Python, Node.js)

### Limites e Cotas
- Tempo máximo de execução: 15 minutos
- Tamanho máximo do pacote: 250 MB
- Espaço em /tmp: 512 MB

## Padrões de Arquitetura

1. **API Gateway + Lambda**
   - Backend para aplicações web
   - Sem gerenciamento de servidores

2. **Lambda com S3**
   - Processamento de uploads
   - Transformação de imagens
   - Geração de thumbnails

3. **Lambda + SQS**
   - Processamento assíncrono
   - Fila de tarefas

## Considerações de Custo

- Gratuito para 1 milhão de requisições/mês
- Cobrança por tempo de execução e memória alocada
- Otimizar tempo e recursos computacionais

## Ferramentas de Desenvolvimento

- AWS SAM (Serverless Application Model)
- AWS CDK
- Serverless Framework
- Zappa (para Python)

## Conclusão

AWS Lambda revoluciona o desenvolvimento de software, permitindo focar na lógica de negócio sem se preocupar com infraestrutura.