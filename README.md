# MedicAI_backend
Repositório base para desenvolvimento do backend MedicAI

# Como iniciar a API 

1. Baixe uma versão do Python maior our igual 3.8 ou maior 

2. Adicione o Poetry como um pacote no seu python (no **terminal** digite) 

```shell
pip install poetry
```

3. Agora inicie, na pasta do ecomm_of_love,o pacote com poetry (no **terminal** digite) 

```shell
poetry install
```

4. configure a Venv 

```shell
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true
poetry config virtualenvs.path .venv
```

5. Inicialize o interpretador Venv criado pelo Poetry 

* Pela [IDE](https://code.visualstudio.com/docs/python/environments)
* Terminal -> Ubuntu/Windows:
```shell
source .venv/bin/activate
```

6. Executar API 

* Pela [IDE](https://code.visualstudio.com/docs/python/environments)
* Terminal -> Ubuntu/Windows:
 ```shell
 python3 main.py
 ``` 

7. Acessar o docs da API

* 0.0.0.0:5000/docs  

# Conceitos podem ser revisados aqui

[FastAPI website](https://fastapi.tiangolo.com/)

[Python POO](https://pythonacademy.com.br/blog/introducao-a-programacao-orientada-a-objetos-no-python)

[Pydantic validação de dados](https://docs.pydantic.dev/latest/)

[SQLalchemy - Banco de dados](https://www.sqlalchemy.org/)

[Poetry](https://python-poetry.org/)