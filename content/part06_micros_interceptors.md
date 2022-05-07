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
