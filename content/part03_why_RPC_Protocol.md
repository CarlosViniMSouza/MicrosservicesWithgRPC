## Por que RPC e buffers de protocolo?

Ok, então por que você deve usar essa sintaxe formal para definir sua API? Se você quiser fazer uma solicitação de um microsserviço para outro, você não pode simplesmente fazer uma [solicitação HTTP](https://realpython.com/python-requests/) e obter uma resposta JSON? Bem, você pode fazer isso, mas há benefícios em usar buffers de protocolo.

### Documentação

O primeiro benefício de usar buffers de protocolo é que eles fornecem à sua API um esquema bem definido e autodocumentado. Se você usa JSON, deve documentar os campos que ele contém e seus tipos. Como acontece com qualquer documentação, você corre o risco de a documentação ser imprecisa ou incompleta ou ficar desatualizada.

Ao escrever sua API na linguagem de buffer de protocolo, você pode gerar código Python a partir dela. Seu código nunca ficará fora de sincronia com sua documentação. [A documentação é boa](https://realpython.com/documenting-python-code/), mas o código autodocumentado é melhor.
