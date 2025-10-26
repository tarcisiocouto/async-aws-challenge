# AWS SQS (Simple Queue Service)

## Visão Geral

AWS SQS (Simple Queue Service) é um serviço de fila de mensagens totalmente gerenciado que permite o desacoplamento e escalabilidade de microsserviços, sistemas distribuídos e aplicações serverless.

## Tipos de Filas

### 1. Fila Padrão (Standard Queue)
- Alto throughput
- Entrega de mensagem pelo menos uma vez
- Ordem não garantida

### 2. Fila FIFO (First-In-First-Out)
- Ordem estrita de mensagens
- Entrega exatamente uma vez
- Suporta deduplicação de mensagens

## Casos de Uso

- Processamento assíncrono de tarefas
- Comunicação entre microsserviços
- Buffering de cargas de trabalho
- Integração de sistemas distribuídos

## Exemplo de Código Python

```python
import boto3
import json

class SQSManager:
    def __init__(self, queue_name):
        self.sqs = boto3.client('sqs')
        self.queue_url = self._get_queue_url(queue_name)

    def _get_queue_url(self, queue_name):
        """Obtém a URL da fila"""
        try:
            response = self.sqs.get_queue_url(QueueName=queue_name)
            return response['QueueUrl']
        except self.sqs.exceptions.QueueDoesNotExist:
            raise ValueError(f"Fila {queue_name} não encontrada")

    def send_message(self, message):
        """Enviar mensagem para a fila"""
        try:
            response = self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message),
                MessageGroupId='default'  # Necessário para filas FIFO
            )
            return response['MessageId']
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            raise

    def receive_messages(self, max_messages=10):
        """Receber mensagens da fila"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20  # Long polling
            )
            return response.get('Messages', [])
        except Exception as e:
            print(f"Erro ao receber mensagens: {e}")
            raise

    def delete_message(self, receipt_handle):
        """Deletar mensagem após processamento"""
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
        except Exception as e:
            print(f"Erro ao deletar mensagem: {e}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    sqs_manager = SQSManager('minha-fila')
    
    # Enviar mensagem
    message = {"task": "processar_pedido", "id": 12345}
    message_id = sqs_manager.send_message(message)
    print(f"Mensagem enviada: {message_id}")

    # Receber e processar mensagens
    messages = sqs_manager.receive_messages()
    for msg in messages:
        body = json.loads(msg['Body'])
        print(f"Processando: {body}")
        sqs_manager.delete_message(msg['ReceiptHandle'])
```

## Melhores Práticas

1. **Configuração de Long Polling**
   - Reduz custos e aumenta eficiência
   - Diminui chamadas à API

2. **Tratamento de Erros**
   - Implemente Dead Letter Queues (DLQ)
   - Configure tempos de visibilidade adequados

3. **Segurança**
   - Criptografar mensagens em repouso
   - Usar IAM Roles com permissões mínimas
   - Habilitar AWS KMS para criptografia

## Considerações de Custo

- Pague apenas pelo que usar
- Otimize tamanho e número de mensagens
- Use Auto Scaling para gerenciar carga

## Monitoramento

- CloudWatch para métricas de fila
- Configurar alarmes para:
  - Número de mensagens
  - Tempo de processamento
  - Erros de processamento

## Conclusão

AWS SQS oferece solução robusta para comunicação assíncrona e escalável entre componentes de sistemas distribuídos.