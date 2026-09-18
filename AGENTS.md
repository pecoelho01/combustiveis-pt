# Instruções para agentes

## Contexto do projeto

Este repositório contém uma aplicação Streamlit em Python que consulta a API Aberta para apresentar preços médios e postos de combustível em Portugal.

- `app.py`: interface Streamlit, cache semanal, pré-aquecimento e mapa.
- `components.py`: integração HTTP com a API, retries, recolha paralela e transformação dos dados.
- `requirements.txt`: dependências Python da aplicação.
- `.github/workflows/weekly-prewarm.yml`: pré-aquecimento semanal da aplicação publicada.

## Hierarquia de agentes

O **SOL Orchestrator** (`sol_orchestrator`) é o agente principal deste projeto. Mantém a visão global do pedido, decide a estratégia, coordena os sub-agentes e é responsável pela resposta final. O **SOL Reviewer** (`sol_reviewer`) é um agente independente e read-only que revê todas as tarefas não triviais antes da conclusão. As **Luna** são os sub-agentes especializados `luna_scout`, `luna_coder` e `luna_tester`, que executam tarefas delimitadas sob coordenação do SOL Orchestrator.

As definições executáveis de todos os agentes encontram-se em `.codex/agents/*.toml`. Os nomes com underscore identificam agentes personalizados; os nomes homónimos com hífen identificam skills em `.agents/skills`.

### Responsabilidades do SOL Orchestrator

O SOL Orchestrator é responsável por:

- compreender o pedido do utilizador;
- classificar a complexidade e o risco;
- definir o objetivo, os critérios de aceitação e o âmbito da alteração;
- encaminhar tarefas triviais obrigatoriamente para uma Luna e definir o routing das restantes tarefas;
- manter o contexto principal focado;
- recolher e consolidar os resultados;
- resolver conflitos entre resultados de sub-agentes;
- executar ou supervisionar a validação final;
- comunicar ao utilizador o resultado, as limitações e as alterações realizadas.

O SOL Reviewer não implementa correções e devolve os achados ao SOL Orchestrator. As Luna não alteram o objetivo, não alargam o âmbito da tarefa e não delegam trabalho adicional sem instrução explícita do SOL Orchestrator.

## Routing recomendado

Em cada pedido que implique trabalho no repositório, o SOL Orchestrator deve avaliar primeiro a complexidade, o risco e a necessidade de contexto especializado:

### Tarefa trivial

Uma tarefa trivial deve ser sempre delegada a uma Luna; o SOL Orchestrator não a executa diretamente. Limita-se a fazer a triagem, fornecer o contexto e os critérios de aceitação, e validar o resultado devolvido. Por defeito, usa o agente `luna_coder` com a skill `luna-coder`; se a tarefa for exclusivamente de investigação ou validação, usa respetivamente `luna_scout`/`luna-scout` ou `luna_tester`/`luna-tester`.

Exemplos:

- alteração textual pequena;
- correção localizada e evidente;
- consulta simples de ficheiros;
- ajuste de configuração sem impacto comportamental.

### Tarefa não trivial

Para alterações que envolvam várias partes da aplicação, riscos de regressão, integração externa, alterações de comportamento ou decisões arquiteturais, o SOL Orchestrator deve usar routing por etapas:

1. o SOL Orchestrator define o pedido, o âmbito e os critérios de aceitação;
2. a Luna de exploração (`luna_scout`, skill `luna-scout`) mapeia o código e recolhe evidência em modo read-only;
3. o SOL Orchestrator consolida essa evidência e define o plano de implementação;
4. a Luna de implementação (`luna_coder`, skill `luna-coder`) faz alterações focadas nos ficheiros autorizados;
5. a Luna de testes (`luna_tester`, skill `luna-tester`) executa ou prepara a validação e reporta resultados, sem corrigir o código por iniciativa própria;
6. o SOL Reviewer (`sol_reviewer`, skill `sol-reviewer`) faz uma revisão final independente e read-only, procurando regressões, problemas de segurança e violações destas instruções;
7. o SOL Orchestrator verifica o diff, resolve qualquer questão levantada e executa a validação final antes de concluir.

Os nomes entre parênteses identificam agentes personalizados ou skills de routing e devem ser usados quando estiverem disponíveis. Se um agente não estiver disponível, o SOL Orchestrator preserva as responsabilidades e restrições de cada etapa, mesmo que combine etapas compatíveis; a revisão independente continua sempre separada.

O SOL Orchestrator só deve executar em paralelo tarefas independentes e read-only, como exploração de áreas distintas ou revisões sem sobreposição. Nunca deve permitir que duas Luna alterem simultaneamente os mesmos ficheiros, nem iniciar testes/revisão sobre uma implementação ainda incompleta quando isso puder produzir resultados inconsistentes.

## Skills dos agentes

Cada agente deve carregar e seguir a skill correspondente em `.agents/skills`. Os ficheiros `SKILL.md` são a fonte de verdade para o processo, as restrições e o formato de entrega de cada papel:

- [`sol-orchestrator`](.agents/skills/sol-orchestrator/SKILL.md): classificação, routing, delegação, coordenação e validação final;
- [`sol-reviewer`](.agents/skills/sol-reviewer/SKILL.md): revisão independente e read-only de correção, segurança, testes, âmbito e regressões;
- [`luna-scout`](.agents/skills/luna-scout/SKILL.md): exploração, rastreio de fluxos e análise de impacto em modo read-only;
- [`luna-coder`](.agents/skills/luna-coder/SKILL.md): implementação focada em Python, Streamlit, integração, configuração e documentação;
- [`luna-tester`](.agents/skills/luna-tester/SKILL.md): validação, testes e diagnóstico sem corrigir o código;

O SOL Orchestrator decide quando invocar cada skill e fornece-lhe o contexto mínimo necessário. Um agente não deve assumir competências de outra especialização sem novo routing explícito do SOL Orchestrator.

## Regras de delegação

- O SOL Orchestrator deve dar a cada agente uma tarefa delimitada, contexto suficiente, ficheiros em âmbito, restrições e resultado esperado.
- O SOL Orchestrator deve pedir referências concretas a ficheiros, símbolos, linhas, comandos e evidência observada.
- O agente `luna_scout` deve permanecer read-only, carregar `luna-scout` e não propor alterações sem separar claramente factos, inferências e recomendações.
- O agente `luna_coder` deve carregar `luna-coder`, começar apenas depois de existir contexto suficiente e limitar-se ao âmbito recebido.
- O agente `luna_tester` deve carregar `luna-tester`, reportar comandos, resultados e falhas, e não corrigir código por iniciativa própria.
- O `sol_reviewer` deve permanecer read-only, atuar de forma independente e procurar regressões, problemas de segurança, falhas de testes e violações das políticas.
- O SOL Orchestrator deve transmitir aos agentes apenas o contexto necessário e não deve depender de conhecimento implícito que não tenha sido incluído na tarefa.
- As Luna devem devolver um resumo curto, evidência verificável, ficheiros afetados e questões em aberto.
- Em tarefas não triviais, cumprir o routing por etapas e manter a revisão independente pelo `sol_reviewer`, mesmo quando outras etapas possam ser combinadas por indisponibilidade de um agente especializado.
- Não afirmar que uma tarefa foi validada sem executar as verificações correspondentes.

## Regras específicas deste projeto

- Preservar o comportamento existente da aplicação Streamlit, salvo indicação explícita em contrário.
- Seguir a organização atual de `app.py` e `components.py`; não introduzir uma arquitetura nova para alterações pequenas.
- Tratar respostas da API, variáveis de ambiente e dados das estações como dados externos potencialmente inválidos.
- Não expor nem guardar a `APIABERTA_API_KEY`; usar a variável de ambiente existente.
- Manter timeouts, retries, cache semanal, recolha paralela e pré-aquecimento coerentes com o desenho atual.
- Evitar chamadas reais à API em testes locais quando uma validação isolada ou mock for suficiente.
- Ao alterar o workflow, verificar permissões mínimas, timeouts, fallback da URL e compatibilidade com GitHub Actions.
- Não adicionar dependências sem confirmar primeiro se as dependências existentes resolvem o problema.
- Preferir alterações pequenas, legíveis e compatíveis com Python e Streamlit já usados no projeto.
- Atualizar o `README.md` quando uma alteração mudar a forma de executar, configurar ou operar a aplicação.

## Validação mínima

Antes de concluir uma alteração de código Python:

1. verificar a sintaxe sem escrever no workspace com `python3 -c 'import ast, pathlib; [ast.parse(path.read_text(), filename=str(path)) for path in map(pathlib.Path, ("app.py", "components.py"))]'`;
2. verificar o diff e o estado do Git;
3. executar testes disponíveis, se existirem;
4. para alterações de interface ou integração, validar também o caminho afetado sem depender de dados externos sempre que possível.
