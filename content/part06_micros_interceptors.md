## Monitoramento de microsserviços Python com interceptores

Depois de ter alguns microsserviços na nuvem, você deseja ter visibilidade de como eles estão se saindo. Algumas coisas que você deseja monitorar incluem:

&nbsp; &nbsp; ° Quantas solicitações cada microsserviço está recebendo

&nbsp; &nbsp; ° Quantas solicitações resultam em erro e que tipo de erro elas geram

&nbsp; &nbsp; ° A latência em cada solicitação

&nbsp; &nbsp; ° Logs de exceção para que você possa depurar mais tarde

Você aprenderá sobre algumas maneiras de fazer isso nas seções abaixo.

### Por que não decoradores

Uma maneira de fazer isso, e a mais natural para desenvolvedores Python, é adicionar um [decorador](https://realpython.com/primer-on-python-decorators/) a cada endpoint de microsserviço. No entanto, neste caso, existem várias desvantagens em usar decoradores:

&nbsp; &nbsp; ° Os desenvolvedores de novos microsserviços precisam se lembrar de adicioná-los a cada método.

&nbsp; &nbsp; ° Se você tem muito monitoramento, então você pode acabar com uma pilha de decoradores.

&nbsp; &nbsp; ° Se você tiver uma pilha de decoradores, os desenvolvedores podem empilhá-los na ordem errada.

&nbsp; &nbsp; ° Você pode consolidar todo o seu monitoramento em um único decorador, mas pode ficar confuso.

Esta pilha de decoradores é o que você quer evitar:

```python
class RecommendationService(recommendations_pb2_grpc.RecommendationsServicer):
    @catch_and_log_exceptions
    @log_request_counts
    @log_latency
    def Recommend(self, request, context):
        ...
```

Ter essa pilha de decoradores em cada método é feio e repetitivo, e viola o [princípio de programação DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself): _Não se Repita_.

Decoradores também são um desafio para escrever, principalmente se aceitam argumentos.

### Interceptores

Há uma abordagem alternativa para o uso de decoradores que você seguirá neste tutorial: o gRPC tem um conceito de **interceptor** que fornece funcionalidade semelhante a um decorador, mas de uma maneira mais limpa.

### Implementando interceptores

Infelizmente, a implementação Python do gRPC tem uma [API bastante complexa para interceptores](https://grpc.github.io/grpc/python/grpc.html#service-side-interceptor). Isso ocorre porque é [incrivelmente flexível](https://github.com/grpc/proposal/blob/master/L13-python-interceptors.md#server-side-implementation). No entanto, existe um pacote [grpc-interceptor](https://pypi.org/project/grpc-interceptor/) para simplificá-los. Para divulgação completa, eu sou o autor.

Adicione-o ao seu arquivo `requirements/requirements.txt` junto com [pytest](https://realpython.com/pytest-python-testing/), que você usará em breve:

```text
grpc-interceptor ~= 0.12.0
grpcio-tools ~= 1.30
pytest ~= 5.4
```

Em seguida, atualize seu ambiente virtual:

```shell
$ python -m pip install recommendations/requirements.txt
```

Agora você pode criar um interceptor com o código a seguir. Você não precisa adicionar isso ao seu projeto, pois é apenas um exemplo:

```python
from grpc_interceptor import ServerInterceptor

class ErrorLogger(ServerInterceptor):
    def intercept(self, method, request, context, method_name):
        try:
            return method(request, context)
        except Exception as e:
            self.log_error(e)
            raise

    def log_error(self, e: Exception) -> None:
        # ...
```

Isso chamará log_error() sempre que uma exceção não tratada em seu microsserviço for chamada. Você pode implementar isso, por exemplo, registrando exceções no Sentry para receber alertas e informações de depuração quando elas ocorrerem.

Para usar este interceptor, você o passaria para grpc.server() assim:

```python
interceptors = [ErrorLogger()]
server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                     interceptors=interceptors)
```

Com esse código, todas as solicitações e respostas do microsserviço Python passarão pelo interceptor, para que você possa contar quantas solicitações e erros ele recebe.

grpc-interceptor também fornece uma exceção para cada código de status gRPC e um interceptor chamado `ExceptionToStatusInterceptor`. Se uma das exceções for levantada pelo microsserviço,
então `ExceptionToStatusInterceptor` definirá o código de status gRPC. Isso permite que você simplifique seu microsserviço fazendo as alterações destacadas abaixo em `recommendations/recommendations.py`:

```python
from grpc_interceptor import ExceptionToStatusInterceptor
from grpc_interceptor.exceptions import NotFound

# ...

class RecommendationService(
    recommendations_pb2_grpc.RecommendationsServicer
):
    def Recommend(self, request, context):
        if request.category not in books_by_category:
            raise NotFound("Category not found")

        books_for_category = books_by_category[request.category]
        num_results = min(request.max_results, len(books_for_category))
        books_to_recommend = random.sample(books_for_category, num_results)

        return RecommendationResponse(recommendations=books_to_recommend)

def serve():
    interceptors = [ExceptionToStatusInterceptor()]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors
    )
    # ...
```

Isso é mais legível. Você também pode gerar a exceção de muitas funções na pilha de chamadas em vez de ter que passar o contexto para poder chamar `context.abort()`. Você também não precisa capturar a exceção em seu microsserviço – o interceptor irá pegá-la para você.

### -> Testando Interceptores

Se você deseja escrever seus próprios interceptores, deve testá-los. Mas é perigoso zombar demais ao testar algo como interceptores. Por exemplo, você pode chamar `.intercept()` no teste e certificar-se de que ele retorne o que você deseja, mas isso não testaria entradas realistas ou que elas fossem chamadas.

Para melhorar os testes, você pode executar um microsserviço gRPC com interceptores. O pacote `grpc-interceptor` fornece uma estrutura para fazer isso. Abaixo, você escreverá um teste para o interceptor `ErrorLogger`. Este é apenas um exemplo, então você não precisa adicioná-lo ao seu projeto. Se você fosse adicioná-lo, você o adicionaria a um arquivo de teste.

Veja como você pode escrever um teste para um interceptor:

```python
from grpc_interceptor.testing import dummy_client, `DummyRequest`, raises

class MockErrorLogger(ErrorLogger):
    def __init__(self):
        self.logged_exception = None

    def log_error(self, e: Exception) -> None:
        self.logged_exception = e

def test_log_error():
    mock = MockErrorLogger()
    ex = Exception()
    special_cases = {"error": raises(ex)}

    with dummy_client(special_cases=special_cases, interceptors=[mock]) as client:
        # Test no exception
        assert client.Execute(`DummyRequest`(input="foo")).output == "foo"
        assert mock.logged_exception is None

        # Test exception
        with pytest.raises(grpc.RpcError) as e:
            client.Execute(`DummyRequest`(input="error"))
        assert mock.logged_exception is ex
```

Aqui está um passo a passo:

&nbsp; &nbsp; ° **Linhas 3 a 8** subclasse `ErrorLogger` para simular `log_error()`. Você realmente não quer que o efeito colateral do registro aconteça. Você só quer ter certeza de que é chamado.

&nbsp; &nbsp; ° As **linhas 15 a 18** usam o gerenciador de contexto `dummy_client()` para criar um cliente conectado a um microsserviço gRPC real. Você envia `DummyRequest` para o microsserviço e ele responde com `DummyResponse`. Por padrão, a entrada de `DummyRequest` é ecoada na saída de `DummyResponse`. No entanto, você pode passar para `dummy_client()` um dicionário de casos especiais, e se a entrada corresponder a um deles, ele chamará uma função que você fornecer e retornará o resultado.

&nbsp; &nbsp; ° **Linhas 21 a 23**: Você testa se `log_error()` é chamado com a exceção esperada. `raises()` retorna outra função que gera a exceção fornecida. Você define a entrada como `error` para que o microsserviço gere uma exceção.

Para obter mais informações sobre testes, você pode ler o [teste eficaz do Python com o Pytest](https://realpython.com/pytest-python-testing/) e o [entendimento da biblioteca de objetos simulados do Python](https://realpython.com/python-mock-library/).

Uma alternativa aos interceptores em alguns casos é usar uma **malha de serviço**. Ele enviará todas as solicitações e respostas de microsserviço por meio de um proxy, para que o proxy possa registrar automaticamente itens como volume de solicitações e contagens de erros. Para obter um registro de erros preciso, seu microsserviço ainda precisa definir os códigos de status corretamente. Então, em alguns casos, seus interceptores podem complementar uma malha de serviço. Uma malha de serviço popular é o [Istio](https://istio.io/latest/docs/concepts/observability/).
