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

Observe que seria melhor gerar uma [exceção em condições](https://realpython.com/python-exceptions/) de erro em vez de usar `abort()` como você faz neste exemplo, mas a resposta não definiria o código de status corretamente. Há uma maneira de contornar isso, que você verá mais tarde no tutorial quando observar os interceptores.

A classe `RecommendationService` define sua implementação de microsserviço, mas você ainda precisa executá-la. É isso que `serve()` faz:

```python
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
        RecommendationService(), server
    )

    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
```

`serve()` inicia um servidor de rede e usa sua classe de microsserviço para lidar com solicitações:

&nbsp; &nbsp; ° A **linha 42** cria um servidor gRPC. Você diz para usar 10 threads para atender solicitações, o que é um exagero total para esta demonstração, mas um bom padrão para um microsserviço Python real.

&nbsp; &nbsp; ° A **linha 43** associa sua classe ao servidor. Isso é como adicionar um manipulador para solicitações.

&nbsp; &nbsp; ° A **linha 46** diz ao servidor para executar na porta 50051. Como mencionado anteriormente, esta é a porta padrão para gRPC, mas você pode usar qualquer coisa que desejar.

&nbsp; &nbsp; ° As **linhas 47 e 48** chamam `server.start()` e `server.wait_for_termination()` para iniciar o microsserviço e esperar até que ele seja interrompido. A única maneira de pará-lo neste caso é digitar `^ Ctrl` + `C` no terminal. Em um ambiente de produção, existem maneiras melhores de desligar, que você verá mais tarde.

Sem fechar o terminal que você estava usando para testar o cliente, abra um novo terminal e execute o seguinte comando:

```shell
$ python recommendations.py
```

Isso executa o microsserviço Recomendações para que você possa testar o cliente em alguns dados reais. Agora retorne ao terminal que você estava usando para testar o cliente para que você possa criar o stub do canal. Se você deixou seu console aberto, pode pular as importações, mas elas são repetidas aqui como uma atualização:

```python
import grpc
from recommendations_pb2_grpc import RecommendationsStub

channel = grpc.insecure_channel("localhost:50051")
client = RecommendationsStub(channel)
```

Agora que você tem um objeto cliente, você pode fazer uma solicitação:

```python
request = RecommendationRequest(
   user_id=1, category=BookCategory.SCIENCE_FICTION, max_results=3)

print(client.Recommend(request))

"""
output:

recommendations {
  id: 6
  title: "The Dune Chronicles"
}
recommendations {
  id: 4
  title: "The Hitchhiker\'s Guide To The Galaxy"
}
recommendations {
  id: 5
  title: "Ender\'s Game"
}
"""
```

Funciona! Você fez uma solicitação de RPC ao seu microsserviço e obteve uma resposta! Observe que a saída que você vê pode ser diferente porque as recomendações são escolhidas aleatoriamente.

Agora que você tem o servidor implementado, você pode implementar o microsserviço Marketplace e fazer com que ele chame o microsserviço Recomendações.

Você pode fechar seu console Python agora, se quiser, mas deixe o microsserviço de recomendações em execução.

### Amarrando-o junto

Crie um novo diretório marketplace/ e coloque um arquivo marketplace.py nele para o microsserviço do Marketplace. Sua árvore de diretórios agora deve ficar assim:

```
.
├── marketplace/
│   ├── marketplace.py
│   ├── requirements.txt
│   └── templates/
│       └── homepage.html
|
├── protobufs/
│   └── recommendations.proto
|
└── recommendations/
    ├── recommendations.py
    ├── recommendations_pb2.py
    ├── recommendations_pb2_grpc.py
    └── requirements.txt
```

Observe o novo diretório `marketplace/` para seu código de microsserviço, `requirements.txt` e uma página inicial. Todos serão descritos a seguir. Você pode criar arquivos vazios para eles por enquanto e preenchê-los mais tarde.

Você pode começar com o código do microsserviço. O microsserviço do Marketplace será um aplicativo [Flask](https://realpython.com/tutorials/flask/) para exibir uma página da Web para o usuário. Ele chamará o microsserviço de recomendações para obter recomendações de livros para exibir na página.

Abra o arquivo `marketplace/marketplace.py` e adicione o seguinte:

Você configura o Flask, cria um cliente gRPC e adiciona uma função para renderizar a página inicial. Aqui está um desdobramento:

&nbsp; &nbsp; ° A **linha 10** cria um aplicativo Flask para renderizar uma página da Web para o usuário.

&nbsp; &nbsp; ° As **linhas 12 a 16** criam seu canal gRPC e stub.

&nbsp; &nbsp; ° As **linhas 20 a 30** criam render_homepage() para ser chamado quando o usuário visitar a página inicial do seu aplicativo. Ele retorna uma página HTML carregada de um modelo, com três recomendações de livros de ficção científica.

Abra o arquivo `homepage.html` em seu diretório `marketplace/templates/` e adicione o seguinte HTML:

```html
<!-- homepage.html -->
<!doctype html>
<html lang="en">
<head>
    <title>Online Books For You</title>
</head>
<body>
    <h1>Mystery books you may like</h1>
    <ul>
    {% for book in recommendations %}
        <li>{{ book.title }}</li>
    {% endfor %}
    </ul>
</body>
```

Esta é apenas uma página inicial de demonstração. Ele deve exibir uma lista de recomendações de livros quando você terminar.

Para executar esse código, você precisará das seguintes dependências, que podem ser adicionadas ao `marketplace/requirements.txt`:

```text
flask ~= 1.1
grpcio-tools ~= 1.30
Jinja2 ~= 2.11
pytest ~= 5.4
```

Os microsserviços `Recommendations` e `Marketplace` terão seus próprios `requirements.txt`, mas por conveniência neste tutorial, você pode usar o mesmo ambiente virtual para ambos. Execute o seguinte para atualizar seu ambiente virtual:

```shell
$ python -m pip install -r marketplace/requirements.txt
```

Para executar seu microsserviço do Marketplace, digite o seguinte em seu console:

```shell
FLASK_APP=marketplace.py flask run
```

Agora você deve ter os microsserviços de Recomendações e Marketplace em execução em dois consoles separados. Se você desligar o microsserviço de recomendações, reinicie-o em outro console com o seguinte (em um terminal shell de Linux/MacOS):

```shell
$ cd recommendations
$ python recommendations.py
```

Isso executa seu aplicativo Flask, que é executado por padrão na porta 5000. Vá em frente e abra-o no seu navegador e confira!

Agora você tem dois microsserviços conversando entre si! Mas eles ainda estão apenas na sua máquina de desenvolvimento. Em seguida, você aprenderá como colocá-los em um ambiente de produção.

Você pode interromper seus microsserviços Python digitando `^Ctrl`+ `C` no terminal em que eles estão sendo executados. Você os executará no [Docker](https://realpython.com/docker-in-action-fitter-happier-more-productive/) a seguir, que é como eles serão executados em um ambiente de produção.
