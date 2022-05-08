## Melhores Práticas

Agora você tem uma configuração de microsserviço Python funcionando. Você pode criar microsserviços, testá-los juntos, implantá-los no Kubernetes e monitorá-los com interceptores. Você pode começar a criar microsserviços neste momento. No entanto, você deve manter algumas práticas recomendadas em mente, para aprender algumas nesta seção.

## Organização Protobuf

Geralmente, você deve manter suas definições de protobuf separadas de sua implementação de microsserviço. Os clientes podem ser escritos em quase qualquer idioma, e se você agrupar seus arquivos protobuf em uma [roda Python](https://realpython.com/python-wheels/) ou algo semelhante, se alguém quiser um cliente Ruby ou Go, será difícil para eles obter os arquivos protobuf.

Mesmo que todo o seu código seja Python, por que alguém precisaria instalar o pacote para o microsserviço apenas para escrever um cliente para ele?

Uma solução é colocar seus arquivos protobuf em um repositório Git separado do código do microsserviço. Muitas empresas colocam _todos_ os arquivos protobuf de todos os microsserviços em um único repositório.

Isso facilita a localização de todos os microsserviços, o compartilhamento de estruturas protobuf comuns entre eles e a criação de ferramentas úteis.
