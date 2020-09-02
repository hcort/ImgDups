import hashlib
import os
import sys

# https://pypi.org/project/python-magic-bin/0.4.14/ > pip install python-magic-bin==0.4.14
import magic
from flask import Flask, Blueprint, request, render_template

app = Flask(__name__)

comparador_trad = Blueprint('comparador_trad', __name__, template_folder='templates')


def procesar_excepcion(ex, full_path='', err_file=None, br='\n', tab='\t'):
    err_msg = ''
    import datetime
    ahora = datetime.datetime.now()
    err_msg += '%s%sExcepción: %s%s' % (str(ahora), tab, ex, br)
    if full_path:
        err_msg += '%s%s%s%s' % (str(ahora), tab, full_path, br)
    err_msg += '%s%sException: %s%s' % (str(ahora), tab, str(ex), br)
    err_msg += '%s%sArgs: %s%s' % (str(ahora), tab, str(ex.args), br)
    import traceback
    err_msg += '%s%sTrace:%s%s%s' % (str(ahora), tab, br, str(traceback.format_exc()), br)
    err_msg += '%s%sExc info:%s%s%s' % (str(ahora), tab, br, str(sys.exc_info()[0]), br)
    print(err_msg)
    if err_file:
        err_file.write('\n\n\n*************************************************\n')
        err_file.write('%s\t%s\n' % (str(ahora), full_path))
        err_file.write('%s\tException: %s\n' % (str(ahora), str(ex)))
        err_file.write('%s\tArgs: %s\n' % (str(ahora), str(ex.args)))
        err_file.write('%s\tTrace:\n%s' % (str(ahora), str(traceback.format_exc())))
        err_file.write('%s\tExc info:\n%s\n' % (str(ahora), str(sys.exc_info()[0])))
        # err_file.write(str(json_obj))
    return err_msg

"""
    Necesito ejecutar un servidor HTTP para poder ver las imágenes en el navegador.
    
    Uso Web Server for Chrome
    https://chrome.google.com/webstore/detail/web-server-for-chrome/ofhbbkphhbklhfoeikjpcbhemlocgigb/related
    
    Y lo arranco en la ruta en la que quiero buscar los archivos duplicados
"""
local_http_server = 'http://127.0.0.1:8887/'


@app.route('/borrar', methods=['GET', 'POST'])
def borrar_dups():
    dups = request.form['lista_dups']
    pass


def listar_directorio_duplicados(path, local_http_root, recursivo=True):
    """

    :param path: el directorio que quiero recorrer
    :param recursivo: búsqueda en subdirectorios
    :return:
    """
    duplicados = {}
    for dir_name_root, sub_dir_root_list, file_root_list in os.walk(path):
        for filename in file_root_list:
            file_path = os.path.join(dir_name_root, filename)
            # C:\Users\Hector\Desktop\bkp
            mgc = magic.from_file(file_path, mime=True)
            if mgc.startswith('image/'):
                # Open,close, read file and calculate MD5 on its contents
                md5_str = ''
                try:
                    with open(file_path, "rb") as file_to_check:
                        # read contents of the file
                        data = file_to_check.read()
                        md5_str = hashlib.md5(data).hexdigest()
                except Exception as err:
                    print('Error leyendo fichero: ' + file_path + '\t' + str(err))
                if md5_str:
                    # http://127.0.0.1:8887
                    # if md5_str in duplicados:
                    #     duplicados[md5_str].append(file_path)
                    # else:
                    #     duplicados[md5_str] = [file_path]
                    relative_path = os.path.relpath(file_path, local_http_root)
                    if md5_str in duplicados:
                        duplicados[md5_str].append(relative_path)
                    else:
                        duplicados[md5_str] = [relative_path]
        if recursivo:
            for subdir in sub_dir_root_list:
                duplicados_sub = listar_directorio_duplicados(subdir, local_http_root, recursivo)
                for k in duplicados_sub:
                    if k not in duplicados:
                        duplicados[k] = []
                    for v in k:
                        duplicados[k].append(v)
    return duplicados


def eliminar_ficheros_no_duplicados(lista_md5):
    # duplicados_f = dict(filter(lambda elem: (len(elem[1]) > 1), lista_md5.items()))
    duplicados = {key: value for (key, value) in lista_md5.items() if (len(value) > 1)}
    return duplicados


@app.route('/check_dups', methods=['GET', 'POST'])
def check_dups():
    if request.method == 'POST':
        # check if the post request has the file part
        duplicados = {}
        err_msg = ''
        try:
            path = request.form['ruta']
            rec = request.form['recursivo']
            if path:
                # filename = secure_filename(path)
                try:
                    lista_ficheros = listar_directorio_duplicados(path, path, recursivo=rec)
                    duplicados = eliminar_ficheros_no_duplicados(lista_ficheros)
                except Exception as err:
                    err_msg = procesar_excepcion(err, br='<br>', tab='&emsp;')
        except Exception as err:
            err_msg = procesar_excepcion(err, br='<br>', tab='&emsp;')
        return render_template('check_grid.html', file_upload=True, lista_dups=duplicados,
                               http_server=local_http_server,
                               error_msg=err_msg)
        pass
    return render_template('check_grid.html', file_upload=True, comparacion=None, error_msg=None)


if __name__ == '__main__':
    app.run()
