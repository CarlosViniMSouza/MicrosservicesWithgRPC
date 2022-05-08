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
