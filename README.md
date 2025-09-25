# EstimatorAI - Ferramenta Inteligente de Planejamento e Estimativa

Uma ferramenta inteligente de planejamento e estimativa de projetos de software que utiliza AWS Bedrock para automatizar:
- Refinamento dos requisitos do cliente (Épicos)
- Determinação das tarefas com o respectivo tempo de execução
- Geração de um plano de trabalho estruturado

## Arquitetura

[Architecture Diagram](architecture.mmd)

## Como Funciona

1. Cliente envia requisitos via API Gateway
2. Lambda Handler retorna ID imediatamente
3. Requisição enviada para SQS Queue
4. Processor Lambda processa com Bedrock (até 15 min)
5. Resultado salvo no S3
6. Cliente consulta resultado quando necessário

## Componentes

- **API Gateway**: Recebe requisições do cliente
- **Lambda Handler**: Gera ID e envia para fila
- **SQS Queue**: Fila de processamento assíncrono
- **Processor Lambda**: Processa estimativas com Bedrock
- **S3 Storage**: Armazena resultados das estimativas
- **Fine Tuning**: Melhora o modelo com dados históricos

## Estrutura do Projeto

```
├── README.md
├── architecture.mmd
├── DEPLOY.md             # Guia de deployment
├── serverless.yml        # Configuração completa
├── api-gateway/          # Configuração do API Gateway
├── lambda-function/      # Lógica de processamento
│   ├── handler.py        # Lambda principal (API)
│   ├── processor.py      # Lambda processador (SQS)
│   └── prompt.md         # Prompt para Bedrock
├── s3-storage/          # Armazenamento de resultados
└── fine-tuning/         # Melhoria do modelo
```

## Pré-requisitos

- Conta AWS com acesso ao Bedrock
- Python 3.9+
- AWS CLI configurado
- Permissões para Lambda, SQS, S3 e Bedrock
