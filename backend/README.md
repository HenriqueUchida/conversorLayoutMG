# Fluxo de Validação e Processamento

O projeto tem como objetivo validar e processar uma planilha de dados fiscais (MG), utilizando como referência uma planilha gerada pelo sistema (Controller).

O processamento será dividido em duas chamadas da API:

1. **Validação dos layouts**
2. **Processamento dos dados**

A segunda etapa somente será executada caso os layouts das duas planilhas estejam corretos.

---

## 1. Validação dos cabeçalhos

Primeira chamada da API.

Nesta etapa serão validados os cabeçalhos das planilhas MG e Controller, verificando se todos os campos obrigatórios estão presentes.

Caso existam campos ausentes, o processamento será interrompido e as inconsistências do layout serão retornadas ao frontend.

Caso os dois layouts estejam corretos, o frontend poderá realizar a segunda chamada da API.

---

## 2. Validação do EAN

Após a validação dos layouts, inicia-se o processamento dos dados da planilha MG.

Serão realizadas as seguintes verificações:

* EAN deve possuir formato numérico válido;
* EAN não pode ser nulo;
* EAN não pode estar duplicado.

As inconsistências encontradas deverão ser identificadas sem interromper o processamento dos demais registros válidos.

---

## 3. Validação do NCM

Serão realizadas as seguintes verificações:

* NCM não pode ser nulo;
* NCM deve possuir pelo menos 8 posições.

---

## 4. Validação dos CSTs

Verificar se os seguintes campos estão preenchidos:

* CST ICMS;
* CST PIS;
* CST COFINS.

---

## 5. Tratamento do EX NCM

Quando o campo EX NCM estiver nulo, seu valor deverá ser preenchido automaticamente com `00`.

---

## 6. Regras de ICMS

As regras serão avaliadas de acordo com o CST informado.

### CST 00

* Alíquota deve ser maior que `0`;
* Redução deve ser `0` ou nula.

### CST 20

* Alíquota deve ser maior que `0`;
* Redução deve ser maior que `0`;
* CBENEF deve estar preenchido.

### CST 40

* Alíquota deve ser igual a `0`;
* Redução deve ser igual a `0`;
* CBENEF deve estar preenchido.

### CST 60

* CEST deve estar preenchido;
* Alíquota e redução não serão validadas.

---

## 7. Regras de PIS e COFINS

Serão implementadas regras específicas para validação dos dados de PIS e COFINS.

> Regras ainda a serem definidas.

---

## 8. Validação do IVA

O campo IVA deverá possuir um valor numérico do tipo `float`.

Valores que não representem um número válido, como `"PAUTA"`, deverão ser tratados como `0`.

---

## 9. Merge com a Controller

Após a validação e tratamento da planilha MG, os dados válidos serão cruzados com a planilha Controller.

Nesta etapa serão realizadas validações relacionadas ao código interno dos produtos.

Não poderá existir mais de uma ocorrência de tributação para o mesmo código interno.

---

## 10. Geração dos arquivos

Ao final do processamento serão gerados dois resultados:

### Controller atualizada

Planilha Controller contendo os dados fiscais válidos provenientes da planilha MG.

### Planilha de inconsistências

Arquivo contendo os registros que apresentaram problemas durante o processamento, permitindo que os dados sejam corrigidos posteriormente.

O processamento não deverá ser interrompido devido a inconsistências individuais. Dessa forma, registros válidos poderão continuar o fluxo enquanto os registros inconsistentes serão direcionados para a planilha de inconsistências.

---

## Fluxo geral

```text
                    FRONTEND
                       │
                       ▼
             1ª chamada da API
                       │
                       ▼
              Validação do Layout
                 ┌─────┴─────┐
                 │           │
              Inválido      Válido
                 │           │
                 ▼           ▼
             Retorna       2ª chamada
             erro API         │
                              ▼
                     Tratamento e validação
                         da planilha MG
                              │
              ┌───────────────┴───────────────┐
              │                               │
           Válidos                       Inconsistentes
              │                               │
              ▼                               ▼
       Merge com Controller          Planilha de
              │                      inconsistências
              ▼
      Validações pós-merge
              │
              ▼
       Controller atualizada
```

## Princípio do processamento

O sistema deverá trabalhar com **processamento parcial**.

Isso significa que a existência de registros inconsistentes não deve impedir o processamento dos registros válidos.

Por exemplo:

```text
2.000 produtos válidos
500 produtos inconsistentes
```

Resultado esperado:

```text
2.000 → continuam o processamento
500   → são direcionados para a planilha de inconsistências
```

Dessa forma, o usuário poderá corrigir somente os registros problemáticos sem precisar interromper ou descartar todo o processamento.
