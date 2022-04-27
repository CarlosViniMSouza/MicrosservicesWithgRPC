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
