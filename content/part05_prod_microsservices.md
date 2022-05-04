## Microsserviços Python prontos para produção

Neste ponto, você tem uma arquitetura de microsserviço Python em execução em sua máquina de desenvolvimento, o que é ótimo para testes. Nesta seção, você o executará na nuvem.

### Docker

O **Docker** é uma tecnologia incrível que permite isolar um grupo de processos de outros processos na mesma máquina. Você pode ter dois ou mais grupos de processos com seus próprios sistemas de arquivos, portas de rede e assim por diante. Você pode pensar nisso como um ambiente virtual Python, mas para todo o sistema e mais seguro.

O Docker é perfeito para implantar um microsserviço Python porque você pode empacotar todas as dependências e executar o microsserviço em um ambiente isolado. Quando você implanta seu microsserviço na nuvem, ele pode ser executado na mesma máquina que outros microsserviços sem que eles pisem uns nos outros. Isso permite uma melhor utilização dos recursos.

Este tutorial não mergulhará profundamente no Docker porque levaria um livro inteiro para cobrir. Em vez disso, você apenas se preparará com o básico necessário para implantar seus microsserviços Python na nuvem. Para obter mais informações sobre o Docker, você pode conferir os [Tutoriais do Python Docker](https://realpython.com/tutorials/docker/).

Antes de começar, se você quiser acompanhar em sua máquina, em seguida, certifique-se de ter o Docker instalado. Você pode baixá-lo no [site oficial](https://docs.docker.com/get-docker/).

Você criará duas **imagens** do Docker, uma para o microsserviço Marketplace e outra para o microsserviço Recomendações. Uma imagem é basicamente um sistema de arquivos mais alguns metadados. Em essência, cada um de seus microsserviços terá um ambiente mini Linux para si. Ele pode gravar arquivos sem afetar o sistema de arquivos real e abrir portas sem entrar em conflito com outros processos.

Para criar suas imagens, você precisa definir um `Dockerfile`. Você sempre começa com uma **imagem base** que contém algumas coisas básicas. Nesse caso, sua imagem base incluirá um interpretador Python. Em seguida, você copiará os arquivos de sua máquina de desenvolvimento para sua imagem do Docker. Você também pode executar comandos dentro da imagem do Docker. Isso é útil para instalar dependências.
