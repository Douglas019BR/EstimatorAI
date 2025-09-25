# Lambda Function - Project Estimation Engine

Processa requisições de estimativa de projeto usando AWS Bedrock.

## Funcionamento

1. Recebe requisitos do projeto
2. Retorna ID imediatamente (200)
3. Processa com Bedrock em background
4. Salva resultado no S3

## Input

```json
{
  "requirements": "Descrição dos requisitos do projeto..."
}
```

## Output (200)

```json
{
  "request_id": "uuid-here",
  "status": "processing"
}
```

## Resultado no S3

Salvo em: `s3://bucket/results/{request_id}.json`

```json
{
  "request_id": "uuid-here",
  "timestamp": "2024-01-01T00:00:00Z",
  "status": "completed",
  "input_requirements": "...",
  "result": {
    "refined_requirements": {...},
    "tasks": [...],
    "work_plan": {...}
  }
}
```

## Environment Variables

- `S3_BUCKET`: Bucket para armazenar resultados

## Dependencies

- boto3 (AWS SDK)
- Permissões: Bedrock, S3
