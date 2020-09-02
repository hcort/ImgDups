import os
from functools import reduce

from app import listar_directorio_duplicados, eliminar_ficheros_no_duplicados


def main():
    # uso los métodos de Flask de manera offline
    path = "C:\\Users\\Hector\\Desktop\\bkp\\"
    lista_ficheros = listar_directorio_duplicados(path, path, recursivo=True)
    # ficheros_totales_k = reduce(lambda x, key: x + len(lista_ficheros[key]), lista_ficheros, 0)
    # puedo iterar sobre los valores porque las claves no me interesan
    ficheros_totales = reduce(lambda x, value: x + len(value), lista_ficheros.values(), 0)
    lista_dups = eliminar_ficheros_no_duplicados(lista_ficheros)
    elim_count = 0
    for dup in lista_dups:
        ficheros = lista_dups[dup]
        for idx, fichero in enumerate(ficheros):
            if idx == 0:
                continue
            os.remove(os.path.join(path, fichero))
            elim_count += 1
    lista_ficheros = listar_directorio_duplicados(path, path, recursivo=True)
    print(lista_ficheros)



# Lanzamos la función principal
if __name__ == "__main__":
    main()