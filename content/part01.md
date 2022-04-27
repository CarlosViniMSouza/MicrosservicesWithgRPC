## Por que Microsserviços?

Imagine que você trabalha no Online Books For You, um popular site de comércio eletrônico que vende livros online. A empresa tem várias centenas de desenvolvedores. 

Cada desenvolvedor está escrevendo código para algum produto ou recurso de back-end, como gerenciar o carrinho do usuário, gerar recomendações, lidar com transações de pagamento, ou lidar com o estoque do armazém.

Agora pergunte a si mesmo, você gostaria de ter todo esse código em um aplicativo gigante? Quão difícil seria entender? Quanto tempo levaria para testar? Como você manteria o código e os esquemas de banco de dados? Definitivamente seria difícil, especialmente porque o negócio tenta se mover rapidamente.

Você não preferiria que o código correspondente aos recursos modulares do produto fosse, bem, modular? Um microsserviço de carrinho para gerenciar carrinhos; Um microsserviço de inventário para gerenciar inventário; um microsserviço para cada serviço específico.

### Modularidade

As mudanças de código geralmente seguem o caminho de menor resistência. Seu amado CEO do Online Books For You quer adicionar um novo recurso compre dois livros e ganhe um grátis. Você faz parte da equipe que foi solicitada a lançá-lo o mais rápido possível. Dê uma olhada no que acontece quando todo o seu código está em um único aplicativo.

Sendo o engenheiro mais inteligente da sua equipe, você menciona que pode adicionar algum código à lógica do carrinho para verificar se há mais de dois livros no carrinho. Nesse caso, você pode simplesmente subtrair o custo do livro mais barato do total do carrinho. Não se preocupe - você faz um pull request.

Em seguida, seu gerente de produto diz que você precisa acompanhar o impacto dessa campanha nas vendas de livros. Isso também é bem direto. Como a lógica que implementa o recurso compre dois e ganhe um está no código do carrinho, você adicionará uma linha no fluxo de checkout que atualiza uma nova coluna no banco de dados de transações para indicar que a venda fez parte da promoção: `buy_two_get_one_free_promo = true`. Feito!

Em seguida, seu gerente de produto lembra que a oferta é válida para apenas um uso por cliente. Você precisa adicionar alguma lógica para verificar se alguma transação anterior tinha esse sinalizador buy_two_get_one_free_promo definido. Ah, e você precisa ocultar o banner da promoção na página inicial, para adicionar esse cheque também. Oh, e você precisa enviar e-mails para pessoas que não usaram a promoção. Adicione isso também.

Vários anos depois, o banco de dados de transações ficou muito grande e precisa ser substituído por um novo banco de dados compartilhado. Todas essas referências precisam ser alteradas. Infelizmente, o banco de dados é referenciado em toda a base de código neste momento. Você considera que na verdade foi um pouco fácil demais adicionar todas essas referências.

É por isso que ter todo o seu código em um único aplicativo pode ser perigoso a longo prazo. Às vezes é bom ter limites.

O banco de dados de transações deve ser acessível apenas a um microsserviço de transações. Então, se você precisar dimensioná-lo, não é tão ruim. Outras partes do código podem interagir com transações por meio de uma API abstrata que oculta os detalhes da implementação. Você pode fazer isso em um único aplicativo - é menos provável que você faça. As mudanças de código geralmente seguem o caminho de menor resistência.

### Flexibilidade

Dividir seu código Python em microsserviços oferece mais flexibilidade. Por um lado, você pode escrever seus microsserviços em diferentes idiomas. Muitas vezes, o primeiro aplicativo da web de uma empresa será escrito em [Ruby](https://www.ruby-lang.org/en/about/) ou [PHP](https://www.php.net/manual/en/intro-whatis.php). Isso não significa que todo o resto também tem que ser!

Você também pode dimensionar cada microsserviço de forma independente. Neste tutorial, você usará um aplicativo Web e um microsserviço de Recomendações como exemplo em execução.

Seu aplicativo da Web provavelmente será [I/O bound](https://en.wikipedia.org/wiki/I/O_bound), buscando dados de um banco de dados e talvez carregando modelos ou outros arquivos do disco. Um microsserviço de Recomendações pode estar fazendo muito processamento de números, tornando-o vinculado à [CPU bound](https://en.wikipedia.org/wiki/CPU-bound). Faz sentido executar esses dois microsserviços Python em hardware diferente.

### Robustez

Se todo o seu código estiver em um aplicativo, você precisará implantá-lo de uma só vez. Este é um grande risco! Isso significa que uma alteração em uma pequena parte do código pode derrubar todo o site.

### Propriedade

Quando uma única base de código é compartilhada por um grande número de pessoas, geralmente não há uma visão clara para a arquitetura do código. Isso é especialmente verdadeiro em grandes empresas, onde os funcionários vêm e vão. Pode haver pessoas que tenham uma visão de como o código deve ser, mas é difícil impor quando qualquer um pode modificá-lo e todos estão se movendo rapidamente.

Um benefício dos microsserviços é que as equipes podem ter a propriedade clara de seu código. Isso torna mais provável que haja uma visão clara para o código e que o código permaneça limpo e organizado. Também deixa claro quem é responsável por adicionar recursos ao código ou fazer alterações quando algo dá errado.
