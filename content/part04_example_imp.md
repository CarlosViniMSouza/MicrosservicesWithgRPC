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

### O servidor RPC

Testar o cliente no console é uma coisa, mas implementar o servidor lá é um pouco demais. Você pode deixar seu console aberto, mas implementará o microsserviço em um arquivo.

Comece com as importações e alguns dados:

```python
# recommendations/recommendations.py
from concurrent import futures
import random

import grpc

from recommendations_pb2 import (
    BookCategory,
    BookRecommendation,
    RecommendationResponse,
)
import recommendations_pb2_grpc

books_by_category = {
    BookCategory.MYSTERY: [
        BookRecommendation(id=1, title="The Maltese Falcon"),
        BookRecommendation(id=2, title="Murder on the Orient Express"),
        BookRecommendation(id=3, title="The Hound of the Baskervilles"),
    ],
    BookCategory.SCIENCE_FICTION: [
        BookRecommendation(
            id=4, title="The Hitchhiker's Guide to the Galaxy"
        ),
        BookRecommendation(id=5, title="Ender's Game"),
        BookRecommendation(id=6, title="The Dune Chronicles"),
    ],
    BookCategory.SELF_HELP: [
        BookRecommendation(
            id=7, title="The 7 Habits of Highly Effective People"
        ),
        BookRecommendation(
            id=8, title="How to Win Friends and Influence People"
        ),
        BookRecommendation(id=9, title="Man's Search for Meaning"),
    ],
}
```

Esse código importa suas dependências e cria alguns dados de exemplo. Aqui está um desdobramento:

&nbsp; &nbsp; ° A **linha 2** importa futuros porque o gRPC precisa de um pool de threads. Você chegará a isso mais tarde.

&nbsp; &nbsp; ° A **linha 3** importa aleatoriamente porque você selecionará livros aleatoriamente para recomendações.

&nbsp; &nbsp; ° A **linha 14** cria o [dicionário](https://realpython.com/python-dicts/) `books_by_category`, em que as chaves são categorias de livros e os valores são [listas](https://realpython.com/python-lists-tuples/) de livros nessa categoria. Em um microsserviço de Recomendações real, os livros seriam armazenados em um banco de dados.

Em seguida, você criará uma classe que implementa as funções de microsserviço:

```python
class RecommendationService(
    recommendations_pb2_grpc.RecommendationsServicer
):
    def Recommend(self, request, context):
        if request.category not in books_by_category:
            context.abort(grpc.StatusCode.NOT_FOUND, "Category not found")

        books_for_category = books_by_category[request.category]
        num_results = min(request.max_results, len(books_for_category))
        books_to_recommend = random.sample(
            books_for_category, num_results
        )

        return RecommendationResponse(recommendations=books_to_recommend)
```

Você criou uma classe com um método para implementar o `Recommend` RPC. Aqui estão os detalhes:

&nbsp; &nbsp; ° A **linha 29** define a classe `RecommendationService`. Esta é a implementação do seu microsserviço. Observe que você subclasse `RecommendationsServicer`. Isso faz parte da integração com o gRPC que você precisa fazer.

&nbsp; &nbsp; ° A **linha 32** define um método `Recommend()` em sua classe. Isso deve ter o mesmo nome que o RPC que você define em seu arquivo protobuf. Ele também recebe um `RecommendationRequest` e retorna um `RecommendationResponse` assim como na definição do protobuf. Também recebe um parâmetro de `context`. O [`context`](https://grpc.github.io/grpc/python/grpc.html#grpc.ServicerContext) permite definir o código de status para a resposta.

&nbsp; &nbsp; ° As **linhas 33 e 34** usam [abort()](https://grpc.github.io/grpc/python/grpc.html#grpc.ServicerContext.abort) para encerrar a solicitação e definir o código de status como `NOT_FOUND` se você obtiver uma categoria inesperada. Como o gRPC é construído sobre HTTP/2, o código de status é semelhante ao código de status HTTP padrão. A configuração permite que o cliente execute ações diferentes com base no código que recebe. Também permite middleware, como sistemas de monitoramento, para registrar quantas solicitações têm erros.

&nbsp; &nbsp; ° As **linhas 36 a 40** escolhem aleatoriamente alguns livros da categoria para recomendar. Certifique-se de limitar o número de recomendações a `max_results`. Você usa `min()` para garantir que você não peça mais livros do que existem, ou então `random.sample` apresentará um erro.

&nbsp; &nbsp; ° A **linha 38** [retorna](https://realpython.com/python-return-statement/) um objeto `RecommendationResponse` com sua lista de recomendações de livros.
