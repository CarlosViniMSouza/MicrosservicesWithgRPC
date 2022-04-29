# Quão pequeno é o "Micro"?

Como os microsserviços devem ser pequenos é um daqueles tópicos que podem desencadear um debate acalorado entre os engenheiros. Aqui estão meus dois centavos: _micro_ é um nome impróprio. Devemos apenas dizer _serviços_. No entanto, neste tutorial, você verá _microsserviços_ usados ​​para consistência.

Tornar os microsserviços muito pequenos pode levar a problemas. Em primeiro lugar, ele realmente anula o propósito de tornar o código modular. O código em um microsserviço deve fazer sentido juntos, assim como os dados e métodos em uma [classe](https://realpython.com/python3-object-oriented-programming/#define-a-class-in-python) fazem sentido juntos.

Para usar classes como analogia, considere objetos de arquivo em Python. O objeto de arquivo tem todos os métodos que você precisa. Você pode [`.read()` e `.write()`](https://realpython.com/read-write-files-python/#reading-and-writing-opened-files) para ele, ou você pode `.readlines()` se quiser. Você não deve precisar de uma classe FileReader e FileWriter. Talvez você esteja familiarizado com linguagens que fazem isso, e talvez você sempre tenha pensado que era um pouco complicado e confuso.

Os microsserviços são iguais. O escopo do código deve parecer correto. Nem muito grande, nem muito pequeno.

Em segundo lugar, os microsserviços são mais difíceis de testar do que o código monolítico. Se um desenvolvedor quiser testar um recurso que abrange muitos microsserviços, ele precisará colocá-los em funcionamento em seu ambiente de desenvolvimento. Isso adiciona atrito. Não é tão ruim com alguns microsserviços, mas se forem dezenas, será um problema significativo.

Acertar o tamanho do microsserviço é uma arte. Uma coisa a observar é que cada equipe deve possuir um número razoável de microsserviços. Se sua equipe tem cinco pessoas, mas vinte microsserviços, isso é uma bandeira vermelha. Por outro lado, se sua equipe trabalha em apenas um microsserviço que também é compartilhado por cinco outras equipes, isso também pode ser um problema.