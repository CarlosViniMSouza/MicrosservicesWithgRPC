## Microsserviços Python prontos para produção

Neste ponto, você tem uma arquitetura de microsserviço Python em execução em sua máquina de desenvolvimento, o que é ótimo para testes. Nesta seção, você o executará na nuvem.

### Docker

O **Docker** é uma tecnologia incrível que permite isolar um grupo de processos de outros processos na mesma máquina. Você pode ter dois ou mais grupos de processos com seus próprios sistemas de arquivos, portas de rede e assim por diante. Você pode pensar nisso como um ambiente virtual Python, mas para todo o sistema e mais seguro.

O Docker é perfeito para implantar um microsserviço Python porque você pode empacotar todas as dependências e executar o microsserviço em um ambiente isolado. Quando você implanta seu microsserviço na nuvem, ele pode ser executado na mesma máquina que outros microsserviços sem que eles pisem uns nos outros. Isso permite uma melhor utilização dos recursos.

Este tutorial não mergulhará profundamente no Docker porque levaria um livro inteiro para cobrir. Em vez disso, você apenas se preparará com o básico necessário para implantar seus microsserviços Python na nuvem. Para obter mais informações sobre o Docker, você pode conferir os [Tutoriais do Python Docker](https://realpython.com/tutorials/docker/).

Antes de começar, se você quiser acompanhar em sua máquina, em seguida, certifique-se de ter o Docker instalado. Você pode baixá-lo no [site oficial](https://docs.docker.com/get-docker/).

Você criará duas **imagens** do Docker, uma para o microsserviço Marketplace e outra para o microsserviço Recomendações. Uma imagem é basicamente um sistema de arquivos mais alguns metadados. Em essência, cada um de seus microsserviços terá um ambiente mini Linux para si. Ele pode gravar arquivos sem afetar o sistema de arquivos real e abrir portas sem entrar em conflito com outros processos.

Para criar suas imagens, você precisa definir um `Dockerfile`. Você sempre começa com uma **imagem base** que contém algumas coisas básicas. Nesse caso, sua imagem base incluirá um interpretador Python. Em seguida, você copiará os arquivos de sua máquina de desenvolvimento para sua imagem do Docker. Você também pode executar comandos dentro da imagem do Docker. Isso é útil para instalar dependências.

### -> Dockerfile de recomendações

Você começará criando a imagem do Docker do microsserviço de recomendações. Crie recomendações/Dockerfile e adicione o seguinte:

```dockerfile
FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY recommendations/ /service/recommendations/
WORKDIR /service/recommendations
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/recommendations.proto

EXPOSE 50051
ENTRYPOINT [ "python", "recommendations.py" ]
```

Aqui está um passo a passo linha por linha:

&nbsp; &nbsp; ° A **linha 1** inicializa sua imagem com um ambiente Linux básico mais a versão mais recente do Python. Neste ponto, sua imagem tem um layout típico de sistema de arquivos Linux. Se você olhasse para dentro, teria `/bin`, `/home` e todos os arquivos básicos que você esperaria.

&nbsp; &nbsp; ° A **linha 3** cria um novo diretório em `/service` para conter seu código de microsserviço.

&nbsp; &nbsp; ° As **linhas 4 e 5** copiam os diretórios `protobufs/` e `recommendations/` em `/service`.

&nbsp; &nbsp; ° A **linha 6** fornece ao Docker uma instrução `WORKDIR /service/recommendations`, que é como fazer um `cd` dentro da imagem. Todos os caminhos que você fornecer ao Docker serão relativos a esse local e, quando você executar um comando, ele será executado neste diretório.

&nbsp; &nbsp; ° A **linha 7** atualiza o [`pip`](https://realpython.com/what-is-pip/) para evitar avisos sobre versões mais antigas.

&nbsp; &nbsp; ° A **linha 8** diz ao Docker para executar `pip install -r requirements.txt` dentro da imagem. Isso adicionará todos os arquivos `grpcio-tools` e quaisquer outros pacotes que você possa adicionar à imagem. Observe que você não está usando um ambiente virtual porque é desnecessário. A única coisa em execução nesta imagem será seu microsserviço, para que você não precise isolar ainda mais seu ambiente.

&nbsp; &nbsp; ° A **linha 9** executa o comando python -m grpc_tools.protoc para gerar os arquivos Python a partir do arquivo protobuf. Seu diretório `/service` dentro da imagem agora se parece com isso:

```
/service/
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

&nbsp; &nbsp; ° A **linha 12** informa ao Docker que você executará um microsserviço na porta 50051 e deseja expor isso fora da imagem.

&nbsp; &nbsp; ° A **linha 13** informa ao Docker como executar seu microsserviço.

Agora você pode gerar uma imagem do Docker a partir do seu Dockerfile. Execute o seguinte comando no diretório que contém todo o seu código, não dentro do diretório `recommendations/`, mas um nível acima dele:

```shell
$ docker build . -f recommendations/Dockerfile -t recommendations
```

Isso criará a imagem do Docker para o microsserviço de Recommendations. Você deve ver alguma saída à medida que o Docker cria a imagem. Agora você pode executá-lo:

```shell
$ docker run -p 127.0.0.1:50051:50051/tcp recommendations
```

Você não verá nenhuma saída, mas seu microsserviço de recomendações agora está sendo executado dentro de um contêiner do Docker. Ao executar uma imagem, você obtém um contêiner. Você pode executar a imagem várias vezes para obter vários contêineres, mas ainda há apenas uma imagem.

A opção `-p 127.0.0.1:50051:50051/tcp` diz ao Docker para encaminhar [conexões TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol) na porta `50051` em sua máquina para a porta `50051` dentro do contêiner. Isso lhe dá a flexibilidade de encaminhar diferentes portas em sua máquina.

Por exemplo, se você estiver executando dois contêineres que executam microsserviços Python na porta `50051`, precisará usar duas portas diferentes em sua máquina host. Isso ocorre porque dois processos não podem abrir a mesma porta ao mesmo tempo, a menos que estejam em contêineres separados.

### -> Dockerfile do Marketplace

Em seguida, você criará sua imagem do Marketplace. Crie `marketplace/Dockerfile` e adicione o seguinte:

```Dockerfile
FROM python

RUN mkdir /service
COPY protobufs/ /service/protobufs/
COPY marketplace/ /service/marketplace/
WORKDIR /service/marketplace
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. \
           --grpc_python_out=. ../protobufs/recommendations.proto

EXPOSE 5000
ENV FLASK_APP=marketplace.py
ENTRYPOINT [ "flask", "run", "--host=0.0.0.0"]
```

Isso é muito semelhante ao Dockerfile de recomendações, com algumas diferenças:

&nbsp; &nbsp; ° A **linha 13** usa `ENV FLASK_APP=marketplace.py` para definir a variável de ambiente FLASK_APP dentro da imagem. Flask precisa disso para funcionar.

&nbsp; &nbsp; ° A **linha 14** adiciona `--host=0.0.0.0` ao comando `flask run`. Se você não adicionar isso, o Flask só aceitará conexões do localhost.

Mas espere, você ainda não está executando tudo no localhost? Bem, na verdade não. Quando você executa um contêiner do Docker, ele é isolado de sua máquina host por padrão. localhost dentro do container é diferente de localhost fora, mesmo na mesma máquina. É por isso que você precisa dizer ao Flask para aceitar conexões de qualquer lugar.

Vá em frente e abra um novo terminal. Você pode criar sua imagem do Marketplace com este comando:

```shell
$ docker build . -f marketplace/Dockerfile -t marketplace
```

Isso cria a imagem do Marketplace. Agora você pode executá-lo em um contêiner com este comando:

```shell
$ docker run -p 127.0.0.1:5000:5000/tcp marketplace
```

Você não verá nenhuma saída, mas seu microsserviço do Marketplace agora está em execução.

### Rede

Infelizmente, mesmo que seus contêineres de Recomendações e Marketplace estejam em execução, se você acessar `http://localhost:5000` em seu navegador, receberá um erro. Você pode se conectar ao seu microsserviço do Marketplace, mas ele não pode mais se conectar ao microsserviço de recomendações. Os contêineres são isolados.

Felizmente, o Docker fornece uma solução para isso. Você pode criar uma rede virtual e adicionar os dois contêineres a ela. Você também pode fornecer nomes DNS para que eles possam se encontrar.

Abaixo, você criará uma rede chamada `microservices` e executará o microsserviço Recomendações nela. Você também fornecerá as `recommendations` de nome DNS. Primeiro, pare os contêineres atualmente em execução com `^Ctrl` + `C`. Em seguida, execute o seguinte:

```shell
$ docker network create microservices
$ docker run -p 127.0.0.1:50051:50051/tcp --network microservices \
             --name recommendations recommendations
```

O comando `docker network create` cria a rede. Você só precisa fazer isso uma vez e, em seguida, pode conectar vários contêineres a ele. Em seguida, você adiciona `‑‑network microservices` ao comando `docker run` para iniciar o contêiner nessa rede. A opção de `‑‑name recommendations` fornece as `recommendations` do DNS.

Antes de reiniciar o contêiner do marketplace, você precisa alterar o código. Isso ocorre porque você codificou `localhost:50051` nesta linha de `marketplace.py`:

```python
recommendations_channel = grpc.insecure_channel("localhost:50051")
```

Agora você deseja se conectar a `recommendations:50051`. Mas em vez de codificá-lo novamente, você pode carregá-lo de uma variável de ambiente. Substitua a linha acima pelas duas seguintes:

```python
recommendations_host = os.getenv("RECOMMENDATIONS_HOST", "localhost")
recommendations_channel = grpc.insecure_channel(
    f"{recommendations_host}:50051"
)
```

Isso carrega o nome do host do microsserviço de recomendações na variável de ambiente `RECOMMENDATIONS_HOST`. Se não estiver definido, você pode padronizá-lo para `localhost`. Isso permite que você execute o mesmo código diretamente em sua máquina ou dentro de um contêiner.

Você precisará reconstruir a imagem do mercado desde que alterou o código. Em seguida, tente executá-lo em sua rede:

```shell
$ docker build . -f marketplace/Dockerfile -t marketplace
$ docker run -p 127.0.0.1:5000:5000/tcp --network microservices \
             -e RECOMMENDATIONS_HOST=recommendations marketplace
```

Isso é semelhante a como você o executou antes, mas com duas diferenças:

1. Você adicionou a opção `‑‑network microservices` para executá-lo na mesma rede que seu microsserviço de recomendações. Você não adicionou uma opção ‑‑name porque, diferentemente do microsserviço de Recomendações, nada precisa procurar o endereço IP do microsserviço do Marketplace. O encaminhamento de porta fornecido por `-p 127.0.0.1:5000:5000/tcp` é suficiente e não precisa de um nome DNS.

2. Você adicionou `-e RECOMMENDATIONS_HOST=recommendations`, que define a variável de ambiente dentro do contêiner. É assim que você passa o nome do host do microsserviço de recomendações para seu código.

Neste ponto, você pode tentar `localhost:5000` em seu navegador mais uma vez, e ele deve ser carregado corretamente. Huzá!

### Docker Compose

É incrível que você possa fazer tudo isso com o Docker, mas é um pouco tedioso. Seria bom se houvesse um único comando que você pudesse executar para iniciar todos os seus contêineres. Felizmente existe! Chama-se `docker-compose` e faz parte do projeto Docker.

Em vez de executar vários comandos para criar imagens, criar redes, e executar contêineres, você pode declarar seus microsserviços em um arquivo YAML:

```yaml
version: "3.8"
services:

    marketplace:
        build:
            context: .
            dockerfile: marketplace/Dockerfile
        environment:
            RECOMMENDATIONS_HOST: recommendations
        image: marketplace
        networks:
            - microservices
        ports:
            - 5000:5000

    recommendations:
        build:
            context: .
            dockerfile: recommendations/Dockerfile
        image: recommendations
        networks:
            - microservices

networks:
    microservices:
```

Normalmente, você coloca isso em um arquivo chamado `docker-compose.yaml`. Coloque isso na raiz do seu projeto:

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
├── recommendations/
│   ├── recommendations.py
│   ├── recommendations_pb2.py
│   ├── recommendations_pb2_grpc.py
│   └── requirements.txt
│
└── docker-compose.yaml
```

Este tutorial não entrará em muitos detalhes sobre a sintaxe, pois está bem documentado em outro lugar. Ele realmente faz a mesma coisa que você já fez manualmente. No entanto, agora você só precisa executar um único comando para abrir sua rede e contêineres:

```shell
$ docker-compose up
```

Quando isso estiver em execução, você poderá novamente abrir `localhost:5000` em seu navegador e tudo deverá funcionar perfeitamente.

Observe que você não precisa expor 50051 no contêiner de `recommendations` quando estiver na mesma rede que o microsserviço do Marketplace, portanto, você pode descartar essa parte.

Se você quiser parar o docker-compose para fazer algumas edições antes de subir, pressione `^Ctrl` + `C`.

### Teste

Para [testar a unidade](https://realpython.com/python-testing/) do microsserviço Python, você pode instanciar sua classe de microsserviço e chamar seus métodos. Aqui está um teste de exemplo básico para sua implementação de `RecommendationService`:

```python
# recommendations/recommendations_test.py
from recommendations import RecommendationService

from recommendations_pb2 import BookCategory, RecommendationRequest

def test_recommendations():
    service = RecommendationService()
    request = RecommendationRequest(
        user_id=1, category=BookCategory.MYSTERY, max_results=1
    )
    response = service.Recommend(request, None)
    assert len(response.recommendations) == 1
```

Aqui está um desdobramento:

&nbsp; &nbsp; ° A **linha 6** instancia a classe como qualquer outra e chama métodos nela.

&nbsp; &nbsp; ° A **linha 11** passa [None](https://realpython.com/null-in-python/) para o contexto, que funciona desde que você não a use. Se você quiser testar caminhos de código que usam o contexto, poderá zombar dele.

O teste de integração envolve a execução de testes automatizados com vários microsserviços não simulados. Então é um pouco mais complicado, mas não é muito difícil. Adicione um arquivo `marketplace/marketplace_integration_test.py`:

```python
from urllib.request import urlopen

def test_render_homepage():
    homepage_html = urlopen("http://localhost:5000").read().decode("utf-8")
    assert "<title>Online Books For You</title>" in homepage_html
    assert homepage_html.count("<li>") == 3
```

Isso faz uma solicitação HTTP para o URL da página inicial e verifica se ele retorna algum HTML com um título e três elementos de marcador `<li>` nele. Este não é o melhor teste, pois não seria muito sustentável se a página tivesse mais, mas demonstra um ponto. Esse teste será aprovado somente se o microsserviço de recomendações estiver funcionando. Você também pode testar o microsserviço do Marketplace fazendo uma solicitação HTTP para ele.

Então, como você executa esse tipo de teste? Felizmente, as boas pessoas do Docker também forneceram uma maneira de fazer isso. Depois de executar seus microsserviços Python com `docker-compose`, você pode executar comandos dentro deles com `docker-compose exec`. Então, se você quiser executar seu teste de integração dentro do contêiner do `marketplace`, você pode executar o seguinte comando:

```shell
$ docker-compose build
$ docker-compose up
$ docker-compose exec marketplace pytest marketplace_integration_test.py
```

Isso executa o comando pytest dentro do contêiner do `marketplace`. Como seu teste de integração se conecta ao `localhost`, você precisa executá-lo no mesmo contêiner que o microsserviço.

### Deploy no Kubernetes

Excelente! Agora você tem alguns microsserviços em execução no seu computador. Você pode ativá-los rapidamente e executar testes de integração em ambos. Mas você precisa colocá-los em um ambiente de produção. Para isso, você usará o [Kubernetes](https://kubernetes.io/docs/concepts/overview/what-is-kubernetes/).

Este tutorial não se aprofunda no Kubernetes porque é um tópico grande, e documentação e tutoriais abrangentes estão disponíveis em outros lugares. No entanto, nesta seção, você encontrará o básico para levar seus microsserviços Python a um cluster Kubernetes na nuvem.

### -> Configurações do Kubernetes

Você pode começar com uma configuração mínima do Kubernetes em `kubernetes.yaml`. O arquivo completo é um pouco longo, mas consiste em quatro seções distintas, então você verá uma a uma:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
    name: marketplace
    labels:
        app: marketplace
spec:
    replicas: 3
    selector:
        matchLabels:
            app: marketplace
    template:
        metadata:
            labels:
                app: marketplace
        spec:
            containers:
                - name: marketplace
                  image: hidan/python-microservices-article-marketplace:0.1
                  env:
                      - name: RECOMMENDATIONS_HOST
                        value: recommendations
```

Isso define uma **Implantação** para o microsserviço do Marketplace. Uma [Implantação](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) informa ao Kubernetes como implantar seu código. O Kubernetes precisa de quatro informações principais:

1. Qual imagem do Docker implantar

2. Quantas instâncias implantar

3. Quais variáveis ​​de ambiente os microsserviços precisam

4. Como identificar seu microsserviço

Você pode informar ao Kubernetes como identificar seu microsserviço usando **rótulos**. Embora não seja mostrado aqui, você também pode informar ao Kubernetes quais recursos de memória e CPU seu microsserviço precisa. Você pode encontrar muitas outras opções na [documentação do Kubernetes](https://kubernetes.io/docs/home/).

Veja o que está acontecendo no código:

&nbsp; &nbsp; ° A **linha 9** informa ao Kubernetes quantos pods devem ser criados para seu microsserviço. Um **pod** é basicamente um ambiente de execução isolado, como uma máquina virtual leve implementada como um conjunto de contêineres. A configuração de `replicas: 3` oferece três pods para cada microsserviço. Ter mais de um permite redundância, permitindo atualizações contínuas sem tempo de inatividade, dimensionar conforme você precisa de mais máquinas e ter `failovers`, caso um fique inativo.

&nbsp; &nbsp; ° A **linha 20** é a imagem do Docker a ser implantada. Você deve usar uma imagem do Docker em um registro de imagem. Para obter sua imagem lá, você deve enviá-la para o registro de imagem. Há instruções sobre como fazer isso ao fazer login em sua conta no Docker Hub.

A implantação do microsserviço de recomendações é muito semelhante:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
    name: recommendations
    labels:
        app: recommendations
spec:
    replicas: 3
    selector:
        matchLabels:
            app: recommendations
    template:
        metadata:
            labels:
                app: recommendations
        spec:
            containers:
                - name: recommendations
                  image: hidan/python-microservices-article-recommendations:0.1
```

A principal diferença é que um usa o nome marketplace e o outro usa `recommendations`. Você também define a variável de ambiente `RECOMMENDATIONS_HOST` na implantação do `marketplace`, mas não na implantação de `recommendations`.

Em seguida, você define um **serviço** para o microsserviço de recomendações. Enquanto uma implantação informa ao Kubernetes como implantar seu código, um serviço informa como rotear solicitações para ele. Para evitar confusão com o termo _serviço_ que é comumente usado para falar sobre microsserviços, você verá a palavra em maiúscula quando usada em referência a um Serviço Kubernetes.

Aqui está a definição de serviço para `recommendations`:

```yaml
---
apiVersion: v1
kind: Service
metadata:
    name: recommendations
spec:
    selector:
        app: recommendations
    ports:
        - protocol: TCP
          port: 50051
          targetPort: 50051
```

Aqui está o que está acontecendo na definição:

&nbsp; &nbsp; ° **Linha 48**: Quando você cria um serviço, o Kubernetes cria essencialmente um nome de host DNS com o mesmo nome dentro do cluster. Assim, qualquer microsserviço em seu cluster pode enviar uma solicitação para recomendações. O Kubernetes encaminhará essa solicitação para um dos pods em sua implantação.

&nbsp; &nbsp; ° **Linha 51**: Esta linha conecta o Serviço ao Deployment. Ele instrui o Kubernetes a encaminhar solicitações de recomendações para um dos pods na implantação de recomendações. Isso deve corresponder a um dos pares de chave-valor nos rótulos da implantação.

O serviço do `marketplace` é semelhante:

```yaml
---
apiVersion: v1
kind: Service
metadata:
    name: marketplace
spec:
    type: LoadBalancer
    selector:
        app: marketplace
    ports:
        - protocol: TCP
          port: 5000
          targetPort: 5000
```

Além dos nomes e portas, há apenas uma diferença. Você notará esse tipo: LoadBalancer aparece apenas no Marketplace Service. Isso ocorre porque o marketplace precisa ser acessível de fora do cluster Kubernetes, enquanto as recomendações só precisam ser acessíveis dentro do cluster.

Agora que você tem uma configuração do Kubernetes, sua próxima etapa é implantá-la!
