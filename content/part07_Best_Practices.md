## Melhores Práticas

Agora você tem uma configuração de microsserviço Python funcionando. Você pode criar microsserviços, testá-los juntos, implantá-los no Kubernetes e monitorá-los com interceptores. Você pode começar a criar microsserviços neste momento. No entanto, você deve manter algumas práticas recomendadas em mente, para aprender algumas nesta seção.

### Organização Protobuf

Geralmente, você deve manter suas definições de protobuf separadas de sua implementação de microsserviço. Os clientes podem ser escritos em quase qualquer idioma, e se você agrupar seus arquivos protobuf em uma [roda Python](https://realpython.com/python-wheels/) ou algo semelhante, se alguém quiser um cliente Ruby ou Go, será difícil para eles obter os arquivos protobuf.

Mesmo que todo o seu código seja Python, por que alguém precisaria instalar o pacote para o microsserviço apenas para escrever um cliente para ele?

Uma solução é colocar seus arquivos protobuf em um repositório Git separado do código do microsserviço. Muitas empresas colocam _todos_ os arquivos protobuf de todos os microsserviços em um único repositório.

Isso facilita a localização de todos os microsserviços, o compartilhamento de estruturas protobuf comuns entre eles e a criação de ferramentas úteis.

### Versão do Protobuf

O controle de versão da API pode ser difícil. O principal motivo é que, se você alterar uma API e atualizar o microsserviço, ainda poderá haver clientes usando a API antiga. Isso é especialmente verdadeiro quando os clientes vivem nas máquinas dos clientes, como clientes móveis ou software de desktop.

Você não pode facilmente forçar as pessoas a atualizar. Mesmo que você pudesse, a latência da rede causa [condições de corrida](https://realpython.com/intro-to-python-threading/#race-conditions) e seu microsserviço provavelmente receberá solicitações usando a API antiga. Boas APIs devem ser compatíveis com versões anteriores ou com versão.

Para obter **compatibilidade com versões anteriores**, Os microsserviços Python usando protobufs versão 3 aceitarão solicitações com campos ausentes. Se você quiser adicionar um novo campo, tudo bem. Você pode implantar o microsserviço primeiro e ele ainda aceitará solicitações da API antiga sem o novo campo. O microsserviço só precisa lidar com isso com elegância.

Se você quiser fazer mudanças mais drásticas, precisará fazer a **versão** de sua API. Protobufs permitem que você coloque sua API em um namespace de pacote, que pode incluir um número de versão. 

Se você precisar alterar drasticamente a API, poderá criar uma nova versão dela. O microsserviço também pode continuar aceitando a versão antiga. 

Isso permite que você lance uma nova versão da API enquanto elimina uma versão mais antiga ao longo do tempo.

Seguindo essas convenções, você pode evitar fazer alterações importantes. Dentro de uma empresa, as pessoas às vezes sentem que fazer alterações em uma API é aceitável porque elas controlam todos os clientes. 

Isso cabe a você decidir, mas esteja ciente de que fazer alterações importantes requer implantações coordenadas de clientes e microsserviços, e isso complica as reversões.

Isso pode ser bom muito cedo no ciclo de vida de um microsserviço, quando não há clientes de produção. No entanto, é bom adquirir o hábito de fazer apenas mudanças ininterruptas, uma vez que seu microsserviço é fundamental para a saúde de sua empresa.

### Protobuf Linting

Uma maneira de garantir que você não faça alterações significativas em seus protobufs é usar um **linter**. Um popular é [`buf`](https://buf.build/docs/introduction). Você pode configurar isso como parte do seu [sistema de CI](https://en.wikipedia.org/wiki/Continuous_integration) para verificar as alterações importantes nas solicitações pull.

### Verificação de tipo de código gerado pelo Protobuf

Mypy é um projeto para verificação de tipo estático de código Python. Se você é novo na verificação de tipo estático em Python, então você pode ler [Python Type Checking](https://realpython.com/python-type-checking/#static-type-checking) para aprender tudo sobre isso.

O código gerado pelo protoc é um pouco complicado e não possui anotações de tipo. Se você tentar digitar, verifique com o Mypy,
então você receberá muitos erros e não detectará erros reais, como nomes de campos com erros ortográficos. Felizmente, as pessoas legais do Dropbox escreveram um [plugin](https://github.com/dropbox/mypy-protobuf) para o compilador protoc gerar stubs de tipo. Eles não devem ser confundidos com stubs gRPC.

Para usá-lo, você pode instalar o pacote `mypy-protobuf` e atualizar o comando para gerar a saída do protobuf. Observe a nova opção `‑‑mypy_out`:

```shell
$ python -m grpc_tools.protoc -I ../protobufs --python_out=. \
         --grpc_python_out=. --mypy_out=. ../protobufs/recommendations.proto
```

A maioria dos seus erros do Mypy devem desaparecer. Você ainda pode receber um erro sobre o pacote grpc não ter informações de tipo. Você pode instalar [stubs do tipo gRPC](https://pypi.org/project/grpc-stubs/) não oficiais ou adicionar o seguinte à sua configuração do Mypy:

```config
[mypy-grpc.*]
ignore_missing_imports = True
```

Você ainda terá a maioria dos benefícios da verificação de tipo, como capturar campos com erros ortográficos. Isso é realmente útil para capturar bugs antes que eles cheguem à produção.

### Desligando graciosamente

Ao executar seu microsserviço em sua máquina de desenvolvimento, você pode pressionar `^Ctrl` + `C` para interrompê-lo. Isso fará com que o interpretador Python gere uma exceção `KeyboardInterrupt`.

Quando o Kubernetes estiver executando seu microsserviço e precisar interrompê-lo para lançar uma atualização, ele enviará um sinal ao seu microsserviço. Especificamente, ele enviará um sinal SIGTERM e aguardará trinta segundos. Se o seu microsserviço não tiver saído até então, ele enviará um sinal `SIGKILL`.

Você pode, e deve, capturar e manipular o `SIGTERM` para que você possa terminar de processar as solicitações atuais, mas recusar as novas. Você pode fazer isso colocando o seguinte código em serve():

```python
from signal import signal, SIGTERM

...

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ...
    server.add_insecure_port("[::]:50051")
    server.start()

    def handle_sigterm(*_):
        print("Received shutdown signal")
        all_rpcs_done_event = server.stop(30)
        all_rpcs_done_event.wait(30)
        print("Shut down gracefully")

    signal(SIGTERM, handle_sigterm)
    server.wait_for_termination()
```

Aqui está um desdobramento:

&nbsp; &nbsp; ° A **linha 1** importa o `signal`, que permite capturar e manipular sinais do Kubernetes ou de quase qualquer outro processo.

&nbsp; &nbsp; ° A **linha 11** define uma função para manipular `SIGTERM`. A função será chamada quando o Python receber o sinal `SIGTERM` e o Python passará dois argumentos. Você não precisa dos argumentos, no entanto, então use *_ para ignorá-los.

&nbsp; &nbsp; ° A **linha 13** chama server.stop(30) para encerrar o servidor normalmente. Ele recusará novas solicitações e aguardará 30 segundos para que as solicitações atuais sejam concluídas. Ele retorna imediatamente, mas retorna um objeto `threading.Event` no qual você pode esperar.

&nbsp; &nbsp; ° A **linha 14** aguarda o objeto `Event` para que o Python não saia prematuramente.

&nbsp; &nbsp; ° A **linha 17** registra seu manipulador.

Quando você implanta uma nova versão do seu microsserviço, o Kubernetes envia sinais para encerrar o microsserviço existente. Lidar com eles para encerrar normalmente garantirá que uma solicitação não seja descartada.
