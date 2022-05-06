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
