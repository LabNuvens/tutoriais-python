![Logo do Lab](https://i.imgur.com/id9h6xi.png)

# `tutoriais-python` [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LabNuvens/tutoriais-python/HEAD)
Esta é uma compilação de guias e exemplos de como lidar com dados de radar, satélite e outros do Laboratório de Física de Nuvens do IAG-USP usando a linguagem Python.

Os tutoriais estão organizados da seguinte forma:  
- Nos arquivos `.ipynb` estão os códigos e explicações relacionadas a cada um dos tópicos;
- Nos arquivos `.md` estão explicações que não necessitam de código.

É possível rodar os arquivos `.ipynb` no [Binder](https://mybinder.org/), no [SciServer](https://sciserver.org/) ou no seu editor de preferência, desde que tenha uma instalação de python associada. Veja mais informações sobre configurar sua própria instalação no tópico **0. Instalacao + Boas Praticas de Uso**.

## Esta não é uma introdução à Python!
Estes tutoriais consideram que você já tenha um conhecimento prévio em Python, principalmente estrutura e análise de dados (listas, tuplas, dicionários, matrizes) e funções. Alguns cursos introdutórios disponíveis que podem ajudar caso você esteja começando com Python são:
- Introdução à Ciência da Computação com Python ([Coursera](https://www.coursera.org/)): [parte 1](https://www.coursera.org/learn/ciencia-computacao-python-conceitos#syllabus) e [parte 2](https://www.coursera.org/learn/ciencia-computacao-python-conceitos-2#syllabus)
- [Python Fundamentos para Análise de Dados](https://www.datascienceacademy.com.br/course?courseid=python-fundamentos) ([Data Science Academy](https://www.datascienceacademy.com.br/pages/home))

## Usando o Binder
Basta clicar no badge "launch binder" ao lado do título do repositório para abrir um ambiente do [Jupyter](https://jupyter.org/) já com as bibliotecas necessárias instaladas. **O processo de criar o ambiente pode levar poucos minutos**.

## Usando o SciServer
1. [Faça o login](https://apps.sciserver.org/login-portal/) a partir de um cadastro ou da conta do Google com o [Globus](https://www.globus.org/);
2. **Se você tem acesso ao grupo do LabNuvens no SciServer:** Acesse a pasta do grupo (a partir de *Groups* ou *Files*) e copie todo o conteúdo para o seu volume pessoal `persistent`   
   **Se você não tem acesso ao grupo do LabNuvens no SciServer:** Baixe o conteúdo deste repositório e faça upload no seu volume pessoal `persistent`;
3. Em _Compute_, crie um container do tipo **SciServer Essentials** selecionando o seu volume pessoal `persistent` como _User Volume_;
4. Abra o container ([Jupyter](https://jupyter.org/)) e um crie um novo Terminal (a partir do menu no canto direito);
5. No terminal, instale as bibliotecas necessárias com os comandos:  
    `conda install -c conda-forge scipy xarray cartopy arm_pyart wradlib`    
    `pip install metpy`;
6. Volte à dashboard do Jupyter (clicando no logo do Jupyter) e navegue até a pasta com o conteúdo (em `Storage/[Seu usuário]/persistent/`).

### Autores

Camila Lopes ([cclopes.me](https://cclopes.me/), camila.lopes@iag.usp.br)