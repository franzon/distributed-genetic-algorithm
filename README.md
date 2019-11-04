# APS Sistemas Distribuídos

## Arquitetura

## Fluxo

1. Clientes escolhem um nome
2. Cliente faz chamada GET para listar tarefas
3. Cliente faz chamada POST para criar uma tarefa
4. Quando uma tarefa é criada, o servidor se inscreve nela
5. Cliente clica em uma tarefa
6. Cliente faz chamada REST para listar as n melhores soluções
7. Cliente inicia a execução do algorítmo
8. Quando cliente encontra uma solução melhor, publica no tópico
9. Quando um cliente recebe uma atualização, atualiza sua lista de melhores soluções 
10. Quando um cliente encontra uma solução, publica no tópico
11. Quando um cliente recebe uma atualização de conclusão, para de executar o algorítmo.
12. Quando o servidor recebe uma atualização de conclusão, fecha a tarefa