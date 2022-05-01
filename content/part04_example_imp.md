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

### O Cliente RPC

O código gerado é algo que apenas uma placa-mãe poderia amar. Ou seja, não é um Python muito bonito. Isso ocorre porque não é realmente feito para ser lido por humanos. Abra um shell Python para ver como interagir com ele:

```python
from recommendations_pb2 import BookCategory, RecommendationRequest

request = RecommendationRequest(
    user_id=1, category=BookCategory.SCIENCE_FICTION, max_results=3
)

print(request.category)
# output: 1
```

Você pode ver que o compilador protobuf gerou tipos Python correspondentes aos seus tipos protobuf. Até agora tudo bem. Você também pode ver que há algum tipo de verificação nos campos:

```python
request = RecommendationRequest(
    user_id="oops", category=BookCategory.SCIENCE_FICTION, max_results=3
)

print(request.category)

"""
output:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'oops' has type str, but expected one of: int, long
"""
```

Isso mostra que você obtém um TypeError se passar o tipo errado para um de seus campos protobuf.

Uma observação importante é que todos os campos no proto3 são opcionais, portanto, você precisará validar se todos estão definidos. Se você deixar um não definido, o padrão será zero para tipos numéricos ou uma string vazia para strings:

```python
request = RecommendationRequest(
    user_id=1, category=BookCategory.SCIENCE_FICTION
)

print(request.max_results)
# output: 0
```

Aqui você obtém 0 porque esse é o valor padrão para campos int não definidos.

Enquanto os protobufs fazem a verificação de tipos para você, você ainda precisa validar os valores reais. Portanto, ao implementar seu microsserviço de Recomendações, você deve validar se todos os campos possuem dados válidos. Isso é sempre verdade para qualquer servidor, independentemente de você usar protobufs, JSON, ou qualquer outra coisa. Sempre valide a entrada.

O arquivo `recommendations_pb2.py` que foi gerado para você contém as definições de tipo. O arquivo `recommendations_pb2_grpc.py` contém a estrutura para um cliente e um servidor. Dê uma olhada nas importações necessárias para criar um cliente:

```python
import grpc
from recommendations_pb2_grpc import RecommendationsStub
```

Você [importa](https://realpython.com/python-import/) o módulo `grpc`, que fornece algumas funções para configurar conexões com servidores remotos. Em seguida, você importa o stub do cliente RPC. É chamado de **stub** porque o próprio cliente não possui nenhuma funcionalidade. Ele chama um servidor remoto e passa o resultado de volta.

Se você olhar para trás em sua definição de protobuf, verá a parte `service Recommendations` {...} no final. O compilador protobuf usa esse nome de microsserviço, Recommendations, e acrescenta `Stub` a ele para formar o nome do cliente, `RecommendationsStub`.

Agora você pode fazer uma solicitação RPC:

```python
channel = grpc.insecure_channel("localhost:50051")
client = RecommendationsStub(channel)

request = RecommendationRequest(
    user_id=1, category=BookCategory.SCIENCE_FICTION, max_results=3
)

print(client.Recommend(request))

"""
output:

Traceback (most recent call last):
  ...
grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:
    status = StatusCode.UNAVAILABLE
    details = "failed to connect to all addresses"
    ...
"""
```

Você cria uma conexão com localhost, sua própria máquina, na porta 50051. Essa porta é a porta padrão para gRPC, mas você pode alterá-la se desejar. Você usará um canal inseguro por enquanto, que não é autenticado e não criptografado, mas aprenderá a usar canais seguros posteriormente neste tutorial. Em seguida, você passa esse canal para seu stub para instanciar seu cliente.

Agora você pode chamar o método de recomendação definido no microsserviço de recomendações. Pense na linha 25 da sua definição de protobuf: rpc `Recommend` (...) retorna (...). É daí que vem o método `Recommend`. Você receberá uma exceção porque não há nenhum microsserviço em execução em `localhost:50051`, então você implementará isso em seguida!

Agora que você tem o cliente resolvido, você olhará para o lado do servidor.
