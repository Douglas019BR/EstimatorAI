# EstimatorAI - Ferramenta Inteligente de Planejamento e Estimativa

Uma ferramenta inteligente de planejamento e estimativa de projetos de software que utiliza AWS Bedrock para automatizar:
- Refinamento dos requisitos do cliente (Épicos)
- Determinação das tarefas com o respectivo tempo de execução
- Geração de um plano de trabalho estruturado

## Arquitetura

![Architecture Diagram](architecture.mmd)

## Como Funciona

1. Cliente envia requisitos via API
2. Lambda retorna ID imediatamente
3. Lambda processa com Bedrock em background
4. Resultado salvo no S3
5. Cliente consulta resultado quando necessário

## Componentes

- **API Gateway**: Recebe requisições do cliente
- **Lambda Function**: Processa estimativas com Bedrock
- **S3 Storage**: Armazena resultados das estimativas
- **Fine Tuning**: Melhora o modelo com dados históricos

## Estrutura do Projeto

```
├── README.md
├── architecture.mmd
├── api-gateway/          # Configuração do API Gateway
├── lambda-function/      # Lógica de processamento
├── s3-storage/          # Armazenamento de resultados
└── fine-tuning/         # Melhoria do modelo
```

## Pré-requisitos

- Conta AWS com acesso ao Bedrock
- Python 3.9+
- AWS CLI configurado
- Permissões para S3 e Lambda
