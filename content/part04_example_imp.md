### Exemplo de Implementação

Depois de toda essa conversa sobre buffers de protocolo, é hora de ver o que eles podem fazer. O termo _buffers de protocolo_ é um bocado, então você verá os **protobufs** abreviados comuns usados ​​neste tutorial daqui para frente.

Como mencionado algumas vezes, você pode gerar código Python a partir de protobufs. A ferramenta é instalada como parte do pacote `grpcio-tools`.

Primeiro, defina sua estrutura de diretório inicial:

```
.
├── protobufs/
│   └── recommendations.proto
|
└── recommendations/
```

O diretório `protobufs/` conterá um arquivo chamado `recommendations.proto`. O conteúdo deste arquivo é o código protobuf acima. Por conveniência, você pode visualizar o código expandindo a seção recolhível abaixo:

```java
syntax = "proto3";

enum BookCategory {
    MYSTERY = 0;
    SCIENCE_FICTION = 1;
    SELF_HELP = 2;
}

message RecommendationRequest {
    int32 user_id = 1;
    BookCategory category = 2;
    int32 max_results = 3;
}

message BookRecommendation {
    int32 id = 1;
    string title = 2;
}

message RecommendationResponse {
    repeated BookRecommendation recommendations = 1;
}

service Recommendations {
    rpc Recommend (RecommendationRequest) returns (RecommendationResponse);
}
```
