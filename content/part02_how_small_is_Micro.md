# Quão pequeno é o "Micro"?

Como os microsserviços devem ser pequenos é um daqueles tópicos que podem desencadear um debate acalorado entre os engenheiros. Aqui estão meus dois centavos: _micro_ é um nome impróprio. Devemos apenas dizer _serviços_. No entanto, neste tutorial, você verá _microsserviços_ usados ​​para consistência.

Tornar os microsserviços muito pequenos pode levar a problemas. Em primeiro lugar, ele realmente anula o propósito de tornar o código modular. O código em um microsserviço deve fazer sentido juntos, assim como os dados e métodos em uma [classe](https://realpython.com/python3-object-oriented-programming/#define-a-class-in-python) fazem sentido juntos.

Para usar classes como analogia, considere objetos de arquivo em Python. O objeto de arquivo tem todos os métodos que você precisa. Você pode [`.read()` e `.write()`](https://realpython.com/read-write-files-python/#reading-and-writing-opened-files) para ele, ou você pode `.readlines()` se quiser. Você não deve precisar de uma classe FileReader e FileWriter. Talvez você esteja familiarizado com linguagens que fazem isso, e talvez você sempre tenha pensado que era um pouco complicado e confuso.

Os microsserviços são iguais. O escopo do código deve parecer correto. Nem muito grande, nem muito pequeno.

Em segundo lugar, os microsserviços são mais difíceis de testar do que o código monolítico. Se um desenvolvedor quiser testar um recurso que abrange muitos microsserviços, ele precisará colocá-los em funcionamento em seu ambiente de desenvolvimento. Isso adiciona atrito. Não é tão ruim com alguns microsserviços, mas se forem dezenas, será um problema significativo.

Acertar o tamanho do microsserviço é uma arte. Uma coisa a observar é que cada equipe deve possuir um número razoável de microsserviços. Se sua equipe tem cinco pessoas, mas vinte microsserviços, isso é uma bandeira vermelha. Por outro lado, se sua equipe trabalha em apenas um microsserviço que também é compartilhado por cinco outras equipes, isso também pode ser um problema.

Aqui estão algumas maneiras de dividir sua hipotética livraria online em microsserviços:

&nbsp; &nbsp; ° O **Marketplace** serve a lógica para o usuário navegar pelo site.

&nbsp; &nbsp; ° O **Carrinho** acompanha o que o usuário colocou no carrinho e o fluxo de checkout.

&nbsp; &nbsp; ° As **Transações** lidam com o processamento de pagamentos e o envio de recibos.

&nbsp; &nbsp; ° O **Inventário** fornece dados sobre quais livros estão em estoque.

&nbsp; &nbsp; ° A **Conta de Usuário** gerencia a inscrição do usuário e os detalhes da conta, como alterar a senha.

&nbsp; &nbsp; ° **Comentários** armazenam classificações de livros e comentários inseridos pelos usuários.

Estes são apenas alguns exemplos, não uma lista exaustiva. No entanto, você pode ver como cada um deles provavelmente pertenceria a sua própria equipe, e a lógica de cada um é relativamente independente. Além disso, se o microsserviço Reviews foi implantado com um bug que causou a falha, então o usuário ainda pode usar o site e fazer compras, apesar de as avaliações não carregarem.

### O trade-off microsserviço-monólito

Os microsserviços nem sempre são melhores do que os monólitos que mantêm todo o seu código em um aplicativo. Geralmente, e especialmente no início de um ciclo de vida de desenvolvimento de software, os monólitos permitem que você se mova mais rapidamente. 

Eles tornam menos complicado compartilhar código e adicionar funcionalidades, e ter que implantar apenas um serviço permite que você leve seu aplicativo aos usuários rapidamente.

A desvantagem é que, à medida que a complexidade cresce, todas essas coisas podem gradualmente tornar o monólito mais difícil de desenvolver, mais lento de implantar e mais frágil. A implementação de um monólito provavelmente economizará tempo e esforço no início, mas pode voltar mais tarde para assombrá-lo.

A implementação de microsserviços em Python provavelmente custará tempo e esforço a curto prazo, mas, se bem feita, pode configurar uma escala melhor a longo prazo. É claro que a implementação de microsserviços muito cedo pode diminuir a velocidade (e nessa etapa, velocidade é algo bem valioso).

O ciclo de inicialização típico do Vale do Silício é começar com um monólito para permitir uma iteração rápida à medida que a empresa encontra um produto adequado aos clientes. Depois que a empresa tiver um produto de sucesso e contratar mais engenheiros, é hora de começar a pensar em microsserviços. 

`NOTA: Não os implemente cedo demais, mas não espere muito.`

### Exemplo de microsserviços

Nesta seção, você definirá alguns microsserviços para seu site Online Books For You. Você [definirá uma API](https://realpython.com/api-integration-in-python/) para eles e escreverá o código Python que os implementa como microsserviços à medida que avança neste tutorial.

Para manter as coisas gerenciáveis, você definirá apenas dois microsserviços:

&nbsp; &nbsp; 1. O Marketplace será um aplicativo web mínimo que exibe uma lista de livros para o usuário.

&nbsp; &nbsp; 2. Recomendações será um microsserviço que fornece uma lista de livros nos quais o usuário pode estar interessado.

Aqui está um diagrama que mostra como seu usuário interage com os microsserviços:

![img-microsservice-schema](https://files.realpython.com/media/microservices.78daee973cc1.png)

Você pode ver que o usuário irá interagir com o microsserviço do Marketplace por meio de seu navegador e o microsserviço do Marketplace irá interagir com o microsserviço de recomendações.

Pense por um momento sobre a API de recomendações. Você deseja que a solicitação de recomendações tenha alguns recursos:

&nbsp; &nbsp; ° **ID do usuário**: você pode usar isso para personalizar as recomendações. No entanto, para simplificar, todas as recomendações neste tutorial serão aleatórias.

&nbsp; &nbsp; ° **Categoria de livro**: para tornar a API um pouco mais interessante, você adicionará categorias de livro, como mistério, autoajuda e assim por diante.

&nbsp; &nbsp; ° **Resultados máximos**: você não quer devolver todos os livros em estoque, então você adicionará um limite à solicitação.

A resposta será uma lista de livros. Cada livro terá os seguintes dados:

&nbsp; &nbsp; ° **ID do livro**: um ID numérico exclusivo para o livro.

&nbsp; &nbsp; ° **Título do livro**: o título que você pode exibir para o usuário.

Um site real teria mais dados, mas você manterá o número de recursos limitado por causa deste exemplo.

Agora você pode definir essa API de forma mais formal, na sintaxe de buffers de protocolo:
