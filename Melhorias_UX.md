# PRD - Melhorias de UX e Visualização

## 1. Contexto
O usuário identificou duas dores principais na interface atual:
1.  **Visualização de Detalhes:** O modal de detalhes exibe um JSON cru, difícil de ler para o usuário final.
2.  **Visualização do PDF:** O layout de duas colunas (50/50) corta o PDF, prejudicando a leitura. O usuário sugere um comportamento de "recolher" a coluna de listas (filtros e evidências) similar ao funcionamento da barra lateral (sidebar).

## 2. Soluções Propostas

### 2.1. Melhoria no Modal de Detalhes
**Problema:** Exibição de `st.json(data)` é técnica demais.
**Solução:** Transformar os dados brutos em uma visualização tabular e formatada.
**Implementação Técnica:**
-   **Tabela Fiscal:** Se a evidência for do tipo `catalogada` (Notas Fiscais), exibir os dados principais (CNPJ, Datas, Valores, Chaves) em um componente de tabela (`st.dataframe` ou `st.table`) ou em um Grid de Métricas (`st.columns`).
-   **Texto Formatado:** Para campos de texto longo (Trechos, Conteúdo), usar `st.markdown` com formatação adequada.
-   **Tratamento de Dados:** Formatar moeda (R$), datas (dd/mm/aaaa) e chaves de acesso antes de exibir.

### 2.2. Bloco "Visualizador PDF" Expansível (Colapso Lateral)
**Problema:** PDF ocupando apenas 50% da tela é insuficiente.
**Solução:** Implementar um botão de alternância (Toggle) que "recolhe" a coluna de evidências, dando 100% de largura ao PDF, mas mantendo a facilidade de voltar.
**Implementação Técnica:**
-   **Botão de Controle:** Substituir o botão de texto "Alternar Modo Foco" por botões ícones mais intuitivos situados no topo da coluna da esquerda (ex: `◀️` para recolher) e flutuando sobre o PDF ou no topo da página quando expandido (ex: `▶️` para expandir filtros).
-   **Persistência de Estado:** Manter o `st.session_state['view_mode']` para controlar se renderizamos `col1, col2` ou apenas o PDF.
-   **UX Refinada:**
    -   *Modo Padrão:* Coluna Esquerda (Evidências) | Coluna Direita (PDF). Botão `◀` no cabeçalho da esquerda.
    -   *Modo Foco:* Apenas PDF (largura total). Botão `▶ Restaurar Lista` no topo do visualizador.

---

## 3. Plano de Desenvolvimento (To-Do)

### Frontend
- [ ] **Refatorar Modal de Detalhes (`show_details`)**
    - [ ] Detectar tipo de evidência (Fiscal vs Textual).
    - [ ] Implementar formatação de moeda e data.
    - [ ] Criar layout visual (Grid/Table) substituindo `st.json`.
- [ ] **Refatorar Layout Principal (Colapso)**
    - [ ] Criar botões de ícone para "Recolher" e "Expandir" a coluna lateral.
    - [ ] Ajustar lógica de renderização para garantir que o PDF ocupe `layout="wide"` real quando focado.

-------------------------------------------------------------------
Lista de melhorias:
Na versão atual precisaremos de tres frentes de requisitos:
1) Criar chatbot especializado no processo atual:
- Na base de cadastro já teremos: Processo em pdf, planilha com mapeamento, planilha catalogada das evidencias, e precisaremos inserir arquivo texto resultado da extração (item 3)
- Após o usuário selecionar o filtro Tipo Evidência ou Busca Textual, com base no resultado (lista de evidencias) para o contexto, será mostrado do lado um chatbot especializado no processo e evidencias filtradas
- Quando o usuário digitar uma pergunta sobre as evidencias filtradas do processo, será enviado ao motor LLM os detalhes das evidencias mais as paginas do processo em texto
- A aplicação vai selecionar as paginas conforme detalhe dos processos, cada evidencia tem a pagina registrada do processo, assim ficará fácil selecionar o texto e enviar junto com os detalhes das evidencias
- O chat será armazenado usando o nome de registro, ou seja, precisaremos dar um nome para cada chat iniciado, assim será possível posteriormente consultar o conteúdo do chat

2) Ao selecionar uma evidencia e clicar em pdf é mostrado do lado a pagina em pdf que temos a evidencia, agora precisaremos criar um botão para que o usuário possa copiar o conteúdo da pagina. Esse botão vai acionar o arquivo processo em texto e copiar o conteúdo da pagina e disponibilizar ao usuário (CTRC c + CTRV v)

3) Atualmente a versão não possibilita o upload do arquivo TEXTO do processo. Iremos então fazer essa opção de upload e a partir disso iremos armazenar o arquivo texto do processo e usá-lo tanto para enviar ao LLM (agente chatbot) quanto disponibilizar para o usuário no botão que sera criado (item 2)




