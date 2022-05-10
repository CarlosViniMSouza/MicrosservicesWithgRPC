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

### Protegendo Canais

Até agora, você tem usado canais gRPC inseguros. Isso significa algumas coisas:

1. O cliente não pode confirmar que está enviando solicitações para o servidor pretendido. Alguém poderia criar um microsserviço impostor e injetá-lo em algum lugar para o qual o cliente pudesse enviar uma solicitação. Por exemplo,
eles podem injetar o microsserviço em um pod para o qual o balanceador de carga enviaria solicitações.

2. O servidor não pode confirmar que o cliente está enviando solicitações para ele. Contanto que alguém possa se conectar ao servidor, ele poderá enviar solicitações arbitrárias de gRPC.

3. O tráfego não é criptografado, portanto, qualquer nó que roteie o tráfego também pode visualizá-lo.

Esta seção descreverá como adicionar autenticação e criptografia [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security).

Você aprenderá duas maneiras de configurar o TLS:

1. A maneira direta, na qual o cliente pode validar o servidor, mas o servidor não valida o cliente.

2. A maneira mais complexa, com TLS mútuo, na qual o cliente e o servidor se validam.

Em ambos os casos, o tráfego é criptografado.

### -> Noções básicas de TLS

Antes de mergulhar, aqui está uma breve visão geral do TLS: Normalmente, um cliente valida um servidor. Por exemplo, quando você visita a Amazon.com, seu navegador valida que é realmente Amazon.com e não um impostor. Para fazer isso, o cliente deve receber algum tipo de garantia de um terceiro confiável, mais ou menos como você pode confiar em uma nova pessoa apenas se tiver um amigo em comum que ateste por ela.

Com o TLS, o cliente deve confiar em uma **autoridade de certificação (CA)**. A CA assinará algo mantido pelo servidor para que o cliente possa verificar. Isso é um pouco como seu amigo em comum assinando uma nota e você reconhecendo a caligrafia dele. Para obter mais informações, consulte [Como funciona a segurança da Internet: TLS, SSL e CA](https://opensource.com/article/19/11/internet-security-tls-ssl-certificate-authority).

Seu navegador confia implicitamente em algumas CAs, que normalmente são empresas como GoDaddy, DigiCert ou Verisign. Outras empresas, como a Amazon, pagam uma CA para assinar um certificado digital para que seu navegador confie nelas.

Normalmente, a CA verificaria se a Amazon é proprietária da Amazon.com antes de assinar seu certificado. Dessa maneira, um impostor não teria uma assinatura em um certificado da Amazon.com e seu navegador bloquearia o site.

Com microsserviços, você não pode realmente pedir a uma CA para assinar um certificado porque seus microsserviços são executados em máquinas internas. A CA provavelmente ficaria feliz em assinar um certificado e cobrar por isso, mas o ponto é que não é prático. 

Nesse caso, sua empresa pode atuar como sua própria CA. O cliente gRPC confiará no servidor se tiver um certificado assinado por sua empresa ou por você se estiver fazendo um projeto pessoal.

### -> Autenticação do servidor

O comando a seguir criará um certificado CA que pode ser usado para assinar o certificado de um servidor:

```shell
$ openssl req -x509 -nodes -newkey rsa:4096 -keyout ca.key -out ca.pem \
              -subj /O=me
```

Isso produzirá dois arquivos:

1. **ca.key** é uma chave privada.

2. **ca.pem** é um certificado público.

Você pode então criar um certificado para seu servidor e assiná-lo com seu certificado de CA:

```shell
$ openssl req -nodes -newkey rsa:4096 -keyout server.key -out server.csr \
              -subj /CN=recommendations
$ openssl x509 -req -in server.csr -CA ca.pem -CAkey ca.key -set_serial 1 \
              -out server.pem
```

Isso produzirá três novos arquivos:

1. **server.key** é a chave privada do servidor.

2. **server.csr** é um arquivo intermediário.

3. **server.pem** é o certificado público do servidor.

Você pode adicionar isso ao Dockerfile do microsserviço de recomendações. É muito difícil adicionar segredos a uma imagem do Docker com segurança, mas há uma maneira de fazer isso com as versões mais recentes do Docker, mostradas destacadas abaixo:

```Dockerfile
# syntax = docker/dockerfile:1.0-experimental
# DOCKER_BUILDKIT=1 docker build . -f recommendations/Dockerfile \
#                     -t recommendations --secret id=ca.key,src=ca.key

FROM python

RUN mkdir /service
COPY infra/ /service/infra/
COPY protobufs/ /service/protobufs/
COPY recommendations/ /service/recommendations/
COPY ca.pem /service/recommendations/

WORKDIR /service/recommendations
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/recommendations.proto
RUN openssl req -nodes -newkey rsa:4096 -subj /CN=recommendations \
                -keyout server.key -out server.csr
RUN --mount=type=secret,id=ca.key \
    openssl x509 -req -in server.csr -CA ca.pem -CAkey /run/secrets/ca.key \
                 -set_serial 1 -out server.pem

EXPOSE 50051
ENTRYPOINT [ "python", "recommendations.py" ]
```

As novas linhas são destacadas. Segue uma explicação:

&nbsp; &nbsp; ° A **linha 1** é necessária para habilitar segredos.

&nbsp; &nbsp; ° As **linhas 2 e 3** mostram o comando de como construir a imagem do Docker.

&nbsp; &nbsp; ° A **linha 11** copia o certificado público da CA na imagem.

&nbsp; &nbsp; ° As **linhas 18 e 19** geram uma nova chave privada e certificado do servidor.

&nbsp; &nbsp; ° As **linhas 20 a 22** carregam temporariamente a chave privada da CA para que você possa assinar o certificado do servidor com ela. No entanto, ele não será mantido na imagem.

Sua imagem agora terá os seguintes arquivos:

&nbsp; &nbsp; ° `ca.pem`

&nbsp; &nbsp; ° `servidor.csr`

&nbsp; &nbsp; ° `server.key`

&nbsp; &nbsp; ° `server.pem`

Agora você pode atualizar `serve()` em `recommendations.py` conforme destacado:

```python
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    recommendations_pb2_grpc.add_RecommendationsServicer_to_server(
        RecommendationService(), server
    )

    with open("server.key", "rb") as fp:
        server_key = fp.read()

    with open("server.pem", "rb") as fp:
        server_cert = fp.read()

    creds = grpc.ssl_server_credentials([(server_key, server_cert)])

    server.add_secure_port("[::]:443", creds)
    server.start()
    server.wait_for_termination()
```

Aqui estão as mudanças:

&nbsp; &nbsp; ° As **linhas 7 a 10** carregam a chave privada e o certificado do servidor.

&nbsp; &nbsp; ° As **linhas 12 e 13** executam o servidor usando TLS. Ele aceitará apenas conexões criptografadas por TLS agora.

Você precisará atualizar `marketplace.py` para carregar o certificado CA. Você só precisa do certificado público no cliente por enquanto, conforme destacado:

```python
recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")

with open("ca.pem", "rb") as fp:
    ca_cert = fp.read()

creds = grpc.ssl_channel_credentials(ca_cert)
recommendations_channel = grpc.secure_channel(
    f"{recommendations_host}:443", creds
)
recommendations_client = RecommendationsStub(recommendations_channel)
```

Você também precisará adicionar COPY `ca.pem /service/marketplace/` ao `Dockerfile` do Marketplace.

Agora você pode executar o cliente e o servidor com criptografia e o cliente validará o servidor. Para simplificar a execução de tudo, você pode usar o `docker-compose`. No entanto, no momento da redação deste artigo, o `docker-compose` não suportava segredos de compilação. Você terá que compilar as imagens do Docker manualmente em vez de com a `docker-compose build`.

No entanto, você ainda pode executar o `docker-compose up`. Atualize o arquivo `docker-compose.yaml` para remover as seções de compilação:

```yaml
version: "3.8"
services:

    marketplace:
        environment:
            RECOMMENDATIONS_HOST: recommendations
        # DOCKER_BUILDKIT=1 docker build . -f marketplace/Dockerfile \
        #                   -t marketplace --secret id=ca.key,src=ca.key
        image: marketplace
        networks:
            - microservices
        ports:
            - 5000:5000

    recommendations:
        # DOCKER_BUILDKIT=1 docker build . -f recommendations/Dockerfile \
        #                   -t recommendations --secret id=ca.key,src=ca.key
        image: recommendations
        networks:
            - microservices

networks:
    microservices:
```

Agora você está criptografando o tráfego e verificando se está se conectando ao servidor correto.
