# DynamoDB: Banco de Dados NoSQL Totalmente Gerenciado

## Visão Geral

Amazon DynamoDB é um serviço de banco de dados NoSQL rápido e flexível, totalmente gerenciado, que oferece desempenho consistente e escalabilidade automática.

## Características Principais

- Baixa latência
- Escalabilidade automática
- Altamente disponível
- Modelo de dados chave-valor e documento
- Consistência forte e eventual

## Modelo de Dados

### Componentes Principais
- **Tabela**: Coleção de itens
- **Item**: Conjunto de atributos
- **Chave Primária**: Identificador único
- **Índices Secundários**: Consultas flexíveis

## Exemplo de Código Python

```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
from decimal import Decimal

class GestorProdutos:
    def __init__(self, nome_tabela='Produtos'):
        """
        Inicialização do gerenciador de produtos
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.tabela = self.dynamodb.Table(nome_tabela)

    def criar_produto(self, dados_produto):
        """
        Criar novo produto no DynamoDB
        """
        try:
            # Gerar ID único
            dados_produto['id'] = str(uuid.uuid4())
            
            # Converter valores numéricos para Decimal
            dados_produto['preco'] = Decimal(str(dados_produto['preco']))
            
            # Inserir item
            response = self.tabela.put_item(
                Item=dados_produto,
                ConditionExpression='attribute_not_exists(id)'
            )
            return dados_produto['id']
        
        except self.dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
            raise ValueError("Produto já existe")
        
        except Exception as e:
            print(f"Erro ao criar produto: {e}")
            raise

    def consultar_produto_por_id(self, produto_id):
        """
        Consultar produto por ID
        """
        try:
            response = self.tabela.get_item(
                Key={'id': produto_id}
            )
            return response.get('Item')
        
        except Exception as e:
            print(f"Erro ao consultar produto: {e}")
            raise

    def atualizar_preco_produto(self, produto_id, novo_preco):
        """
        Atualizar preço de um produto
        """
        try:
            response = self.tabela.update_item(
                Key={'id': produto_id},
                UpdateExpression='SET preco = :val',
                ExpressionAttributeValues={
                    ':val': Decimal(str(novo_preco))
                },
                ReturnValues='UPDATED_NEW'
            )
            return response['Attributes']
        
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            raise

    def consulta_produtos_por_categoria(self, categoria):
        """
        Consultar produtos por categoria usando índice secundário
        """
        try:
            response = self.tabela.query(
                IndexName='categoria-index',
                KeyConditionExpression=Key('categoria').eq(categoria),
                Limit=50  # Limitar resultados
            )
            return response.get('Items', [])
        
        except Exception as e:
            print(f"Erro na consulta por categoria: {e}")
            raise

# Exemplo de uso
def main():
    gestor = GestorProdutos()
    
    # Criar produto
    novo_produto = {
        'nome': 'Smartphone X',
        'categoria': 'Eletrônicos',
        'preco': 1999.99,
        'estoque': 50
    }
    produto_id = gestor.criar_produto(novo_produto)
    print(f"Produto criado: {produto_id}")

    # Consultar produto
    produto = gestor.consultar_produto_por_id(produto_id)
    print(f"Detalhes do Produto: {produto}")

if __name__ == '__main__':
    main()
```

## Estratégias de Modelagem

1. **Modelo de Dados Eficiente**
   - Minimize o número de tabelas
   - Use chaves compostas
   - Projete para padrões de acesso

2. **Índices Secundários**
   - Global Secondary Indexes (GSI)
   - Local Secondary Indexes (LSI)

## Melhores Práticas

1. **Modelagem**
   - Projete para padrões de acesso
   - Use chaves compostas
   - Minimize consultas entre tabelas

2. **Performance**
   - Use chaves de partição uniformemente distribuídas
   - Evite hot keys
   - Implemente cache (DAX - DynamoDB Accelerator)

3. **Custos**
   - Use modo de capacidade sob demanda
   - Configure TTL para dados expirados
   - Monitore unidades de capacidade

## Padrões de Projeto

- Tabela única com chaves compostas
- Desnormalização de dados
- Padrão de design: Fan-out

## Segurança

- IAM Roles e Policies
- Criptografia em repouso (AWS KMS)
- VPC Endpoints
- CloudTrail para auditoria

## Casos de Uso

- Aplicações móveis
- Jogos
- IoT
- Microserviços
- Sessões de usuário
- Catálogos de produtos

## Monitoramento

- CloudWatch Metrics
- CloudWatch Logs
- AWS X-Ray
- DynamoDB Streams para auditoria

## Ferramentas de Desenvolvimento

- AWS Console
- AWS CLI
- Frameworks (Serverless, AWS SAM)
- Ferramentas de migração

## Conclusão

DynamoDB oferece solução de banco de dados NoSQL altamente escalável e performática para aplicações modernas.