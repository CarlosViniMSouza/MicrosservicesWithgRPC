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

&nbsp; &nbsp; ° A linha 9 executa o comando python -m grpc_tools.protoc para gerar os arquivos Python a partir do arquivo protobuf. Seu diretório /service dentro da imagem agora se parece com isso: