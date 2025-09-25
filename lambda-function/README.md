# Lambda Functions - Project Estimation Engine

Duas funções Lambda para processamento assíncrono de estimativas de projeto.

## Arquitetura

1. **Handler Lambda**: Recebe requisições via API Gateway
2. **Processor Lambda**: Processa estimativas via SQS

## Handler Lambda (`handler.py`)

### Funcionamento
1. Recebe requisitos do projeto + considerações especiais
2. Gera ID único da requisição
3. Envia mensagem para SQS Queue
4. Retorna ID imediatamente (200)

### Input
```json
{
  "requirements": "Descrição dos requisitos do projeto...",
  "additional_considerations": "Pontos de atenção específicos..."
}
```

### Output (200)
```json
{
  "request_id": "uuid-here",
  "status": "processing"
}
```

## Processor Lambda (`processor.py`)

### Funcionamento
1. Recebe mensagens do SQS Queue
2. Processa com Bedrock (até 15 minutos)
3. Salva resultado no S3

### Timeout
- **Handler**: 30 segundos
- **Processor**: 15 minutos (900s)

## Resultado no S3

Salvo em: `s3://bucket/results/{request_id}.json`

```json
{
  "request_id": "uuid-here",
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "completed",
  "input_requirements": "...",
  "additional_considerations": "...",
  "result": {
    "refined_requirements": {...},
    "risk_analysis": {...},
    "tasks": [...],
    "work_plan": {...}
  }
}
```

## Environment Variables

- `S3_BUCKET`: Bucket para armazenar resultados
- `SQS_QUEUE_URL`: URL da fila SQS

## Dependencies

- boto3 (AWS SDK)
- Permissões: Bedrock, S3, SQS
