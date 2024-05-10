# Gemini Easy Extractor

Extraia dados formatados em qualquer modelo JSON automaticamente, a partir de informações de qualquer arquivo de texto tais como livros, jornais, documentos.

## Perigo!
Lembre-se de nunca enviar arquivos com informações confidenciais para a versão gratuita do API do Gemini, uma vez que os dados enviados para ele [são usados para treinar os modelos da Google](https://ai.google.dev/gemini-api/terms#data-use-unpaid).

A qualidade do output não é perfeita - É necessário que uma pessoa valide, e possivelmente até rode multiplas vezes depois escolha o melhor resultado. Não use para processos que requerem um alto nivel de qualidade.

Até onde eu observei testando o projeto, os nomes e as descrições dos Modelos de Dados e das Funções de Modelo precisam ser escritos em Inglês para que o Gemini funcione corretamente, porém você pode usar Português para a Prompt (tanto a instrução quanto o documento de referencia) e para a descrição dos campos do modelo.

Esse não é um projeto oficial do Google, apesar da versão voltada a programadores se inserir no namespace deles.

# Instruções de uso

## Colab (recomendado)

Eu recomendo usar a versão do Google Colab, especialmente caso você não esteja acostumado a programar:
- English version: https://gist.github.com/etrotta/566da8c1e0e7a4110d7fede740644539
- Português Brasileiro: https://gist.github.com/etrotta/7c87f9ebeab0554769a518ef6d0bcfd2

Alguns detalhes podem diferir entre as versões do Notebook em Inglês, Português e a versão para uso fora do Colab. Algumas dessas mudanças são para acomodar a audiencia alvo de cada uma das versões.

## Pacote de Python

Esse projeto não está disponivel no pypi, não use `pip install <project_name>` normalmente.
Para instalar, você precisa baixar diretamente do repositorio:

```
pip install git+https://github.com/etrotta/gemini_easy_extractor/#subdirectory=gemini_easy_extractor
```

Se você quer usar ele dessa forma, favor referir à [pasta de exemplos](examples), e confira o arquivo [meta.txt](meta.txt) para ver algumas anotações a respeito dos dados de entrada e saida do exemplo.

Ele se insere dentro do namespace dos pacotes "google", criando um novo subpacote "third_party_gemini_extensions", então para usar fora do Colab você tem que importar da seguinte forma depois de instalar do repositorio:

```py
from google.third_party_gemini_extensions import gemini_easy_extractor
# or
from google.third_party_gemini_extensions.gemini_easy_extractor import (
    FunctionGroup,
    create_gemini_model,
    extract_document_information,
)
```
