## Por que RPC e buffers de protocolo?

Ok, então por que você deve usar essa sintaxe formal para definir sua API? Se você quiser fazer uma solicitação de um microsserviço para outro, você não pode simplesmente fazer uma [solicitação HTTP](https://realpython.com/python-requests/) e obter uma resposta JSON? Bem, você pode fazer isso, mas há benefícios em usar buffers de protocolo.

### Documentação

O primeiro benefício de usar buffers de protocolo é que eles fornecem à sua API um esquema bem definido e autodocumentado. Se você usa JSON, deve documentar os campos que ele contém e seus tipos. Como acontece com qualquer documentação, você corre o risco de a documentação ser imprecisa ou incompleta ou ficar desatualizada.

Ao escrever sua API na linguagem de buffer de protocolo, você pode gerar código Python a partir dela. Seu código nunca ficará fora de sincronia com sua documentação. [A documentação é boa](https://realpython.com/documenting-python-code/), mas o código autodocumentado é melhor.

### Validação

O segundo benefício é que, ao gerar código Python a partir de buffers de protocolo, você obtém alguma validação básica de graça. Por exemplo, o código gerado não aceitará campos do tipo errado. O código gerado também tem todo o clichê RPC embutido.

Se você usar HTTP e/ou JSON para sua API, precisará escrever um pequeno código que construa a solicitação; a envie ao servidor, aguarde a resposta; verifique o código de status; analise e valide a resposta. Com buffers de protocolo, você pode gerar código que se parece com uma chamada de função normal, mas faz uma solicitação de rede sob o capô.

Você pode obter esses mesmos benefícios usando estruturas HTTP e JSON, como [Swagger](https://swagger.io/about/) e [RAML](https://raml.org/about-raml). Para um exemplo do Swagger em ação, confira [Python REST APIs With Flask, Connexion e SQLAlchemy](https://realpython.com/flask-connexion-rest-api/).

Então, existem razões para usar o gRPC em vez de uma dessas alternativas? A resposta ainda é sim.

### Performace

A estrutura gRPC [geralmente é mais eficiente](https://www.yonego.com/nl/why-milliseconds-matter/) do que usar solicitações HTTP típicas. O gRPC é construído em cima do [HTTP/2](https://en.wikipedia.org/wiki/HTTP/2), que pode fazer várias solicitações em paralelo em uma conexão de longa duração de maneira segura para threads. 

A configuração da conexão é relativamente lenta, portanto, fazer isso uma vez e compartilhar a conexão em várias solicitações economiza tempo. As mensagens gRPC também são binárias e menores que JSON. Além disso, o HTTP/2 possui compactação de cabeçalho integrada.

O gRPC tem suporte integrado para solicitações e respostas de streaming. Ele gerenciará problemas de rede com mais facilidade do que uma conexão HTTP básica, reconectando-se automaticamente mesmo após longas desconexões. Ele também possui **interceptores**. Você pode até implementar plugins no código gerado, que as pessoas fizeram para produzir [dicas de tipo Python](https://realpython.com/python-type-checking/#hello-types).

### Facilidade para desenvolvedores

Provavelmente, a razão mais interessante pela qual muitas pessoas preferem gRPC em vez de REST é que você pode definir sua API em termos de [funções](https://realpython.com/defining-your-own-python-function/), não de verbos e recursos HTTP. 

Como engenheiro, você está acostumado a pensar em termos de chamadas de função, e é exatamente assim que as APIs gRPC se parecem.

A funcionalidade de mapeamento em uma API REST geralmente é complicada. Você precisa decidir quais são seus recursos, como construir caminhos e quais verbos usar. Muitas vezes, há várias opções, como aninhar recursos ou usar POST ou algum outro verbo. REST vs gRPC pode se transformar em um [debate sobre preferências](https://cloud.google.com/blog/products/api-management/understanding-grpc-openapi-and-rest-and-when-to-use-them). 

Um nem sempre é melhor que o outro, então use o que melhor se adequar ao seu caso de uso.

Estritamente falando, _buffers de protocolo_ referem-se ao formato de serialização de dados enviados entre dois microsserviços. Portanto, os buffers de protocolo são semelhantes a JSON ou XML, pois são formas de formatar dados. 

Ao contrário do JSON, os buffers de protocolo têm um esquema estrito e são mais compactos quando enviados pela rede. Por outro lado, a infraestrutura RPC é, na verdade, chamada **gRPC**, ou Google RPC. Isso é mais parecido com HTTP. Na verdade, como mencionado acima, o gRPC é construído sobre HTTP/2.
