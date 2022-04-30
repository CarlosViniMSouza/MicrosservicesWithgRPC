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

Você vai gerar código Python para interagir com isso dentro do diretório recomendações/. Primeiro, você deve instalar `grpcio-tools`. Crie o arquivo recommendations/requirements.txt e adicione o seguinte:

```text
grpcio-tools ~= 1.30
```

`NOTE: Depois de alguns procedimentos ...`

Isso gera vários arquivos Python do arquivo `.proto`. Aqui está um desdobramento:

&nbsp; &nbsp; ° **python -m grpc_tools.protoc** executa o compilador protobuf, que irá gerar código Python a partir do código protobuf.

&nbsp; &nbsp; ° **-I ../protobufs** informa ao compilador onde encontrar os arquivos que seu código protobuf importa. Na verdade, você não usa o recurso de importação, mas o -
Eu sinalizar é necessário, no entanto.

&nbsp; &nbsp; ° **--python_out=. --grpc_python_out=.** informa ao compilador onde produzir os arquivos Python. Como você verá em breve, ele gerará dois arquivos e você poderá colocar cada um em um diretório separado com essas opções, se desejar.

&nbsp; &nbsp; ° **../protobufs/recommendations.proto** é o caminho para o arquivo protobuf,
que será usado para gerar o código Python.

Olhe a pasta `recommendations`, você verá que 2 novos arquivos (`recommendations_pb2.py` `recommendations_pb2_grpc.py`) foram criados.

Esses arquivos incluem tipos e funções do Python para interagir com sua API. O compilador gerará o código do cliente para chamar um RPC e o código do servidor para implementar o RPC. Você vai olhar para o lado do cliente primeiro.
