# Amazon RDS: Banco de Dados Relacional Gerenciado

## Visão Geral

Amazon RDS (Relational Database Service) fornece um serviço de banco de dados relacional gerenciado que simplifica a configuração, operação e escalabilidade de bancos de dados relacionais na nuvem.

## Motores de Banco de Dados Suportados

- MySQL
- PostgreSQL
- MariaDB
- Oracle
- Microsoft SQL Server
- Amazon Aurora

## Arquitetura e Características

### Componentes Principais
- **Instância de Banco de Dados**: Ambiente de banco de dados isolado
- **Snapshots**: Backups point-in-time
- **Multi-AZ**: Alta disponibilidade
- **Read Replicas**: Escalabilidade de leitura

## Exemplo de Código Python com SQLAlchemy e RDS

```python
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import ClientError

# Gerenciamento de Segredos com AWS Secrets Manager
def obter_credenciais_banco():
    """
    Recuperar credenciais de banco de dados do AWS Secrets Manager
    """
    segredo_nome = 'producao/bancoDados/credenciais'
    
    try:
        cliente_secrets = boto3.client('secretsmanager')
        resposta = cliente_secrets.get_secret_value(SecretId=segredo_nome)
        return eval(resposta['SecretString'])
    
    except ClientError as e:
        print(f"Erro ao recuperar segredos: {e}")
        raise

class GerenciadorBancoDados:
    Base = declarative_base()

    class Produto(Base):
        """
        Modelo de Produto para demonstração
        """
        __tablename__ = 'produtos'
        
        id = Column(Integer, primary_key=True)
        nome = Column(String(100), nullable=False)
        preco = Column(Float, nullable=False)
        categoria = Column(String(50))

    def __init__(self):
        """
        Inicializar conexão com banco de dados RDS
        """
        try:
            # Obter credenciais do Secrets Manager
            credenciais = obter_credenciais_banco()
            
            # Construir string de conexão
            conexao = (
                f"postgresql://{credenciais['username']}:{credenciais['password']}@"
                f"{credenciais['host']}:{credenciais['port']}/{credenciais['dbname']}"
            )
            
            # Criar engine
            self.engine = create_engine(
                conexao, 
                pool_pre_ping=True,  # Teste de conexão
                pool_size=10,         # Tamanho do pool de conexões
                max_overflow=20        # Conexões extras permitidas
            )
            
            # Criar sessão
            self.Session = sessionmaker(bind=self.engine)
            
            # Criar tabelas se não existirem
            self.Base.metadata.create_all(self.engine)
        
        except SQLAlchemyError as e:
            print(f"Erro de conexão: {e}")
            raise
        
        except Exception as e:
            print(f"Erro geral: {e}")
            raise

    def adicionar_produto(self, nome, preco, categoria):
        """
        Adicionar novo produto ao banco de dados
        """
        try:
            with self.Session() as sessao:
                novo_produto = self.Produto(
                    nome=nome, 
                    preco=preco, 
                    categoria=categoria
                )
                sessao.add(novo_produto)
                sessao.commit()
                return novo_produto.id
        
        except SQLAlchemyError as e:
            print(f"Erro ao adicionar produto: {e}")
            raise

    def consultar_produtos_por_categoria(self, categoria):
        """
        Consultar produtos por categoria
        """
        try:
            with self.Session() as sessao:
                produtos = sessao.query(self.Produto).filter_by(categoria=categoria).all()
                return [
                    {
                        'id': p.id, 
                        'nome': p.nome, 
                        'preco': p.preco
                    } for p in produtos
                ]
        
        except SQLAlchemyError as e:
            print(f"Erro na consulta: {e}")
            raise

# Exemplo de uso
def main():
    try:
        gerenciador = GerenciadorBancoDados()
        
        # Adicionar produtos
        id_produto = gerenciador.adicionar_produto(
            'Notebook Pro', 5999.99, 'Eletrônicos'
        )
        print(f"Produto adicionado: {id_produto}")
        
        # Consultar produtos
        produtos_eletronicos = gerenciador.consultar_produtos_por_categoria('Eletrônicos')
        print("Produtos Eletrônicos:")
        for produto in produtos_eletronicos:
            print(produto)
    
    except Exception as e:
        print(f"Erro no processamento: {e}")

if __name__ == '__main__':
    main()
```

## Estratégias de Configuração

1. **Tipos de Instância**
   - Otimizadas para memória
   - Otimizadas para computação
   - Propósito geral

2. **Escalabilidade**
   - Vertical: Aumentar tamanho da instância
   - Horizontal: Read Replicas

## Melhores Práticas

1. **Segurança**
   - Usar VPC
   - Configurar grupos de segurança
   - Criptografia em repouso e em trânsito
   - Multi-Factor Authentication

2. **Performance**
   - Índices otimizados
   - Monitoramento de métricas
   - Configuração adequada de parâmetros

3. **Backup e Recuperação**
   - Snapshots automáticos
   - Retenção de backups
   - Teste de recuperação

## Padrões de Arquitetura

- Single Database
- Multi-AZ
- Read Replica
- Sharding

## Casos de Uso

- Aplicações empresariais
- E-commerce
- Sistemas de gestão
- Análise de dados
- Aplicações com esquema de dados complexo

## Monitoramento

- CloudWatch Metrics
- Performance Insights
- Enhanced Monitoring
- Logs de auditoria

## Considerações de Custo

- Modelo de pagamento por uso
- Reserva de instâncias
- Otimização de tamanho
- Desligar instâncias não utilizadas

## Ferramentas

- AWS Console
- AWS CLI
- AWS SDK
- Ferramentas de migração de dados

## Conclusão

Amazon RDS oferece solução robusta e gerenciada para bancos de dados relacionais, simplificando operações e permitindo foco na lógica de negócio.