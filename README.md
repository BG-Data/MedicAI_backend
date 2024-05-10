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

* 0.0.0.0:8000/docs  



# Como realizar migrações/modificações no db

> Migrações de banco de dados: 

* Usamos Alembic, um pacote python focado em migrar. [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)


1. Utilizando a biblioteca Alembic, podemos iniciar revisões auto geradas (obs: isso funciona para grande maioria das operações, mas não todas. Conferir na doc da [biblioteca](https://alembic.sqlalchemy.org/en/latest/autogenerate.html))

2. Executar uma revisão de modelo no terminal/prompt e na pasta em que se encontra o **alembic.ini** 

```shell
alembic revision --autogenerate -m '[Texto sobre migração]'
```
Gerará um código de migração (ela não foi feita ainda) para o banco de dados

3. Para subir/aplicar as alterações 

```shell
alembic upgrade head
```

4. Para retornar/recuperar o que foi modificado (retornar tudo)

```shell
alembic downgrade base 
```

4. 1 para retornar à algo especifico (revision id é gerada no alembic revision e armazenada na pasta versions)

```shell
alembic downgrade [REVISION_ID] 
```


# Conceitos podem ser revisados aqui

[FastAPI website](https://fastapi.tiangolo.com/)

[Python POO](https://pythonacademy.com.br/blog/introducao-a-programacao-orientada-a-objetos-no-python)

[Pydantic validação de dados](https://docs.pydantic.dev/latest/)

[SQLalchemy - Banco de dados](https://www.sqlalchemy.org/)

[Poetry](https://python-poetry.org/)