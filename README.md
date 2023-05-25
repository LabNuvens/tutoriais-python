![Logo do Lab](https://i.imgur.com/id9h6xi.png)

# `tutoriais-python` 
Esta é uma compilação de guias e exemplos de como lidar com dados de radar, satélite e outros do [Laboratório de Física de Nuvens do IAG-USP](http://labnuvens.iag.usp.br) usando a linguagem Python.

Os tutoriais estão organizados da seguinte forma:  
- Nos arquivos `.ipynb` estão os códigos e explicações relacionadas a cada um dos tópicos;
- Nos arquivos `.md` estão explicações que não necessitam de código.

É possível rodar os arquivos `.ipynb` no [Binder](https://mybinder.org/), no [SciServer](https://sciserver.org/) ou no seu editor de preferência, desde que tenha uma instalação de python associada. Veja mais informações sobre configurar sua própria instalação no tópico **0. Instalacao + Boas Praticas de Uso**.

## Esta não é uma introdução à Python!
Estes tutoriais consideram que você já tenha um conhecimento prévio em Python, principalmente estrutura e análise de dados (listas, tuplas, dicionários, matrizes) e funções. Alguns cursos introdutórios disponíveis que podem ajudar caso você esteja começando com Python estão [listados na página do laboratório](https://sites.google.com/iag.usp.br/labnuvens/dados-e-materiais).

## Usando o Binder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/LabNuvens/tutoriais-python/HEAD)  
Basta clicar no badge acima para abrir um ambiente do [Jupyter](https://jupyter.org/) já com as bibliotecas necessárias instaladas. **O processo de criar o ambiente pode levar alguns minutos**.  


## Usando o Google Colab
[![Siga o passo-a-passo](https://i.imgur.com/yoNYUg9.png)](https://scribehow.com/shared/Usando_tutoriais-python_no_Google_Colab__5AKgjLMVSwqrW3tuvsoXUw)

## Usando o SciServer
1. [Faça o login](https://apps.sciserver.org/login-portal/) a partir de um cadastro ou da conta do Google com o [Globus](https://www.globus.org/);
2. Baixe o conteúdo deste repositório e faça upload no seu volume pessoal `persistent`;
3. Em _Compute_, crie um container do tipo **SciServer Essentials** selecionando o seu volume pessoal `persistent` como _User Volume_;
4. Abra o container ([Jupyter](https://jupyter.org/)) e um crie um novo Terminal (a partir do menu no canto direito);
5. No terminal, instale as bibliotecas necessárias com os comandos:  
    `conda install -c conda-forge scipy xarray cartopy arm_pyart wradlib`    
    `pip install metpy`;
6. Volte à dashboard do Jupyter (clicando no logo do Jupyter) e navegue até a pasta com o conteúdo (em `Storage/[Seu usuário]/persistent/`).

## Sobre o [Jupyter](https://jupyter.org/)
O Jupyter é um ambiente de desenvolvimento em diversas linguagens de programação, construído primeiramente para Python. A versão mais simples, o Jupyter Notebook, é um navegador web que permite o desenvolvimento de códigos com texto [Markdown](https://www.markdownguide.org/) e código integrados no formato `.ipynb`. Aprenda mais sobre como configurar e usar o Jupyter Notebook [neste capítulo do curso de introdução à ciência de dados terrestres do Earth Lab](https://www.earthdatascience.org/courses/intro-to-earth-data-science/open-reproducible-science/jupyter-python/) e [neste capítulo do curso de fundamentos do Projeto Pythia](https://foundations.projectpythia.org/foundations/jupyterlab.html).

---

### Autores

Camila Lopes ([cclopes.netlify.app](https://cclopes.netlify.app/), camila.lopes@iag.usp.br)
