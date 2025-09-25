# API Gateway

Configuração do API Gateway para receber requisições de estimativa.

## Endpoint

**POST /estimate**
- Recebe requisitos do projeto
- Retorna ID da requisição
- Inicia processamento assíncrono

## Configuração

- Integração com Lambda Function
- Timeout: 30 segundos
- CORS habilitado
- Rate limiting conforme necessário

## Deploy

Use AWS CLI ou Console para criar e configurar o API Gateway apontando para a Lambda Function.
