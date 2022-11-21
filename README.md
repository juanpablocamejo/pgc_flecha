# pgc_flecha
Trabajo práctico de Parseo y generación de código

Dependencias:
- [Python v3.10.0](https://www.python.org/downloads)
- pytest v7.1.3
- ply v3.11

Instalación de paquetes:

```console
pip install ply pytest
```

Ejecución de los tests:

```console
py -m pytest -v
```

Ejemplos de ejecución del main:

```console
py src/main.py --tokenize <input>
py src/main.py --tokenize-file <input_file>

```
```console
py src/main.py --parse <input>
py src/main.py --parse-file <input_file>
```