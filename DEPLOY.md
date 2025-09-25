# Deployment Guide

## Pré-requisitos

```bash
# Instalar Serverless Framework
npm install -g serverless

# Instalar plugin para Python
npm install serverless-python-requirements

# Configurar AWS CLI
aws configure
```

## Deploy

```bash
# Deploy completo (Lambdas + API Gateway + SQS + S3)
serverless deploy

# Deploy apenas função específica
serverless deploy function -f estimate
serverless deploy function -f processor
```

## Recursos Criados

- **Lambda Handler**: `estimator-ai-dev-estimate` (30s timeout)
- **Lambda Processor**: `estimator-ai-dev-processor` (15min timeout)
- **API Gateway**: Endpoint POST `/estimate`
- **SQS Queue**: `estimator-ai-queue-dev`
- **S3 Bucket**: `estimator-ai-results-dev`
- **IAM Roles**: Permissões para Bedrock, S3 e SQS

## Fluxo de Processamento

1. **Cliente** → POST `/estimate`
2. **Handler Lambda** → Retorna ID + envia para SQS
3. **SQS Queue** → Trigger Processor Lambda
4. **Processor Lambda** → Bedrock + S3
5. **Cliente** → Consulta resultado no S3

## Endpoints

```
POST https://xxxxxxx.execute-api.us-east-1.amazonaws.com/dev/estimate
```

## Teste

```bash
curl -X POST https://your-api-url/dev/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": "Sistema de login com autenticação",
    "additional_considerations": "Equipe júnior, prazo apertado"
  }'
```

## Monitoramento

```bash
# Logs Handler Lambda
serverless logs -f estimate --tail

# Logs Processor Lambda
serverless logs -f processor --tail

# Monitorar SQS Queue
aws sqs get-queue-attributes --queue-url YOUR_QUEUE_URL --attribute-names All
```

## Cleanup

```bash
serverless remove
```
