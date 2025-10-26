# Amazon S3: Armazenamento de Objetos Escalável

## Visão Geral

Amazon S3 (Simple Storage Service) é um serviço de armazenamento de objetos altamente escalável, seguro e de alto desempenho, projetado para diversas aplicações e casos de uso.

## Características Principais

- Armazenamento ilimitado
- Alta durabilidade
- Baixa latência
- Escalabilidade
- Segurança robusta
- Integração com outros serviços AWS

## Níveis de Armazenamento

1. **S3 Standard**
   - Uso geral
   - Alta disponibilidade
   - Baixa latência

2. **S3 Intelligent-Tiering**
   - Otimização automática de custos
   - Movimentação entre camadas

3. **S3 Glacier**
   - Arquivamento de longo prazo
   - Baixo custo
   - Recuperação sob demanda

## Exemplo de Código Python Completo

```python
import boto3
import os
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import uuid
import mimetypes

class GestorArquivosS3:
    def __init__(self, bucket_name: str):
        """
        Inicializar cliente S3
        
        :param bucket_name: Nome do bucket S3
        """
        self.s3_client = boto3.client('s3')
        self.s3_resource = boto3.resource('s3')
        self.bucket_name = bucket_name

    def upload_arquivo(
        self, 
        caminho_arquivo: str, 
        chave_s3: Optional[str] = None,
        metadados: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Upload de arquivo para S3 com tratamentos avançados
        
        :param caminho_arquivo: Caminho local do arquivo
        :param chave_s3: Chave personalizada no S3 (opcional)
        :param metadados: Metadados customizados (opcional)
        :return: Informações sobre upload
        """
        try:
            # Gerar chave única se não for fornecida
            if not chave_s3:
                nome_arquivo = os.path.basename(caminho_arquivo)
                extensao = os.path.splitext(nome_arquivo)[1]
                chave_s3 = f"uploads/{uuid.uuid4()}{extensao}"

            # Detectar mime type
            mime_type, _ = mimetypes.guess_type(caminho_arquivo)
            mime_type = mime_type or 'application/octet-stream'

            # Metadados padrão
            metadados = metadados or {}
            metadados['original_filename'] = os.path.basename(caminho_arquivo)

            # Upload
            upload_response = self.s3_client.upload_file(
                Filename=caminho_arquivo,
                Bucket=self.bucket_name,
                Key=chave_s3,
                ExtraArgs={
                    'ContentType': mime_type,
                    'Metadata': metadados,
                    'ACL': 'private'  # Restrito por padrão
                }
            )

            # Obter URL assinada com tempo limitado
            url_assinada = self.gerar_url_assinada(chave_s3, tempo_expiracao=3600)

            return {
                'sucesso': True,
                'chave': chave_s3,
                'url_temporaria': url_assinada,
                'mime_type': mime_type
            }

        except ClientError as e:
            print(f"Erro no upload: {e}")
            return {'sucesso': False, 'erro': str(e)}

    def gerar_url_assinada(
        self, 
        chave_s3: str, 
        tempo_expiracao: int = 3600
    ) -> str:
        """
        Gerar URL assinada com tempo de expiração
        
        :param chave_s3: Chave do objeto no S3
        :param tempo_expiracao: Tempo de validade em segundos
        :return: URL assinada
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': chave_s3},
                ExpiresIn=tempo_expiracao
            )
            return url
        except ClientError as e:
            print(f"Erro ao gerar URL assinada: {e}")
            return None

    def download_arquivo(
        self, 
        chave_s3: str, 
        caminho_local: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download de arquivo do S3
        
        :param chave_s3: Chave do objeto no S3
        :param caminho_local: Caminho para salvar (opcional)
        :return: Informações sobre download
        """
        try:
            # Caminho local padrão se não fornecido
            if not caminho_local:
                caminho_local = os.path.join(
                    os.getcwd(), 
                    os.path.basename(chave_s3)
                )

            # Download
            self.s3_client.download_file(
                Bucket=self.bucket_name,
                Key=chave_s3,
                Filename=caminho_local
            )

            return {
                'sucesso': True,
                'caminho_local': caminho_local
            }

        except ClientError as e:
            print(f"Erro no download: {e}")
            return {'sucesso': False, 'erro': str(e)}

    def listar_objetos(
        self, 
        prefixo: Optional[str] = None, 
        limite: int = 100
    ) -> list:
        """
        Listar objetos no bucket
        
        :param prefixo: Filtrar por prefixo
        :param limite: Limite de objetos
        :return: Lista de objetos
        """
        try:
            parametros = {
                'Bucket': self.bucket_name,
                'MaxKeys': limite
            }
            
            if prefixo:
                parametros['Prefix'] = prefixo

            response = self.s3_client.list_objects_v2(**parametros)
            
            return [
                {
                    'chave': obj['Key'],
                    'tamanho': obj['Size'],
                    'ultima_modificacao': obj['LastModified']
                } for obj in response.get('Contents', [])
            ]

        except ClientError as e:
            print(f"Erro ao listar objetos: {e}")
            return []

# Exemplo de uso
def main():
    gestor = GestorArquivosS3('meu-bucket-exemplo')
    
    # Upload de arquivo
    resultado_upload = gestor.upload_arquivo(
        '/caminho/local/arquivo.pdf', 
        metadados={'projeto': 'tutorial-aws'}
    )
    print("Upload:", resultado_upload)

    # Listar objetos
    objetos = gestor.listar_objetos(prefixo='uploads/')
    print("Objetos no bucket:", objetos)

if __name__ == '__main__':
    main()
```

## Melhores Práticas

1. **Segurança**
   - Usar criptografia no servidor
   - Habilitar versionamento
   - Configurar políticas de acesso restritivas
   - Usar AWS KMS para chaves de criptografia

2. **Performance**
   - Usar prefixos para particionamento
   - Habilitar transferência acelerada
   - Considerar CloudFront para distribuição

3. **Custo**
   - Usar ciclos de vida
   - Mover para camadas mais baratas
   - Excluir objetos não utilizados

## Padrões de Arquitetura

- Hospedagem de sites estáticos
- Backup e recuperação
- Armazenamento de dados de aplicações
- Distribuição de mídia

## Casos de Uso

- Hospedagem de sites
- Backup corporativo
- Armazenamento de dados de big data
- Repositório de imagens/vídeos
- Data lakes

## Segurança Avançada

- Políticas de bucket
- ACLs
- Criptografia
- VPC Endpoints
- Controle de acesso por IAM

## Monitoramento

- CloudWatch Metrics
- CloudTrail
- AWS Config
- Event Notifications

## Ferramentas de Gerenciamento

- AWS Console
- AWS CLI
- S3 Browser
- Ferramentas de migração de dados

## Conclusão

Amazon S3 oferece solução de armazenamento de objetos altamente escalável, segura e flexível para diversos casos de uso na nuvem.