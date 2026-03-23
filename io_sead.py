#! /usr/bin/env python3

import numpy as np
import pandas as pd
from datetime import datetime
import xlrd

"""
El original de este archivo se encuentra en CinePy/modules/

Revisar que se esté trabajando con la última versión

"""


def lectura_SEAD_RA3_bin(file_names, variables=[], panda=True, formato='datetime',
                     region=False):
    """
    Función para leer los archivo guardados por el SEAD del RA3 binarios

    Las variables que se guardan son:
    (columna) (identificación)          (descripción)
        0   Fecha y hora
        1   LOG M1                        Corriente logarítmico de marcha 1
        2   LOG M2                        Corriente logarítmico de marcha 2
        3   LOG M3                        Corriente logarítmico de marcha 3
        4   TASA M3                       Tasa de crecimiento de marcha 3
        5   LIN M3                        Corriente lineal de marcha 3
        6   CIP                           Corriente CIP
        7   DELTA P                       Delta P
        8   LIN M4                        Corriente lineal de marcha 4
        9   QP                            Caudal del primario
        10  TEN 1                         Temperatura de entrada al núcleo 1
        11  TSN 1                         Temperatura de salida al núcleo 1
        12  TEN 3                         Temperatura de entrada al núcleo 3
        13  TSN 3                         Temperatura de salida al núcleo 3
        14  MA SB                         Monitor de área sala de bombas
        15  MA PC                         Monitor de área ¿?
        16  MA TM                         Monitor de área telem-anipuladores
        17  MA BT1                        Monitor de área boca de tanque 1
        18  MA BT2                        Monitor de área boca de tanque 2
        19  MA BT3                        Monitor de área boca de tanque 3
        20  MA CO                         Monitor de área consola
        21  CI N16-1                      Corriente de cámara 1 de N16
        22  CI N16-2                      Corriente de cámara 2 de N16
        23  TEN 2                         Temperatura de entrada al núcleo 2
        24  TSN 2                         Temperatura de salida al núcleo 2
        25  LOG A1                        Cuentas logarítmico de arranque 1
        26  LOG A2                        Cuentas logarítmico de arranque 2
        27  LOG A3                        Cuentas logarítmico de arranque 3
        28  TASA A1                       Tasa de cuentas de arranque 1
        29  TASA A2                       Tasa de cuentas de arranque 2
        30  COND                          ?
        31  BC1                           Porcentaje de extracción de barra 1
        32  BC4                           Porcentaje de extracción de barra 4
        33  REACTIV                       Reactividad calculada con LIN M4

    Notas:
        MA TM era originalmente LAB52
        TEN 2 figura como DELTA T1 usando RA3Convert
        TSN 2 figura como DELTA T3 usando RA3Covnert
        REACTIV Nno se escribe usand RA3Convert

    Parámetros
    ----------
        file_names: string or list of strings
            Nombre(s) de el(los) archivo(s) .RA3 que se quiere(n) leer
            Si es una lista, concatena los archivos en el orden en que se
            ingresan. Es últil para leer archivos consecutivos en el tiempo.
        variables: list of strings
            Nombre de las variables que se quieren leer. Si no se especifica
            nada se devuelven todas las variables disponibles
        panda: boolean
            Si es True, devuelve un dataframe con todas las variables
            Si es False, devuelve un array de datetime y otro array de numpy
            con el resto de las variables.
        formato: string ('datetime', 'time')
            Indica el formato de la primer columna. 'datetime' es fecha + hora.
            'time' es sólo hora
        region: ['start', 'end'] in 'datetetime' format
            Especifica el intervalo temporal que se quiere leer.
            Ejemplo: ["2023-03-10 14:35", "2023-03-10 16:00"]
            Si se desea sólo un inicio o fin, poner el otro valor fuera del
            rango de/los archivos leidos.
            Sólo se puede utilizar cuando formato='datetime'.


    Resultados
    ----------
        df: pandas dataframe (sólo si panda=True)
            Dataframe con las columnas leidas
        datetime, data_nparray: datetime array, numpy array (sólo si
                                panda=False)

    """
    # Diccionario para asociar columnas con variables
    label_to_int = {
                    'LOG M1': 1,    # Corriente logarítmico de marcha 1
                    'LOG M2': 2,    # Corriente logarítmico de marcha 2
                    'LOG M3': 3,    # Corriente logarítmico de marcha 3
                    'TASA M3': 4,   # Tasa de crecimiento de marcha 3
                    'LIN M3': 5,    # Corriente lineal de marcha 3
                    'CIP': 6,       # Corriente CIP
                    'DELTA P': 7,   # Delta P
                    'LIN M4': 8,    # Corriente lineal de marcha 4
                    'QP': 9,        # Caudal del primario
                    'TEN 1': 10,    # Temperatura de entrada al núcleo 1
                    'TSN 1': 11,    # Temperatura de salida al núcleo 1
                    'TEN 3': 12,    # Temperatura de entrada al núcleo 3
                    'TSN 3': 13,    # Temperatura de salida al núcleo 3
                    'MA SB': 14,    # Monitor de área sala de bombas
                    'MA PC': 15,    # Monitor de área ¿?
                    'MA TM': 16,    # Monitor de área telem-anipuladores (originalmente LAB52")
                    'MA BT1': 17,   # Monitor de área boca de tanque 1
                    'MA BT2': 18,   # Monitor de área boca de tanque 2
                    'MA BT3': 19,   # Monitor de área boca de tanque 3
                    'MA CO': 20,    # Monitor de área consola
                    'CI N16-1': 21, # Corriente de cámara 1 de N16
                    'CI N16-2': 22, # Corriente de cámara 2 de N16
                    'TEN 2': 23,    # Temperatura de entrada al núcleo 2
                    'TSN 2': 24,    # Temperatura de salida al núcleo 2
                    'LOG A1': 25,   # Cuentas logarítmico de arranque 1
                    'LOG A2': 26,   # Cuentas logarítmico de arranque 2
                    'LOG A3': 27,   # Cuentas logarítmico de arranque 3
                    'TASA A1': 28,  # Tasa de cuentas de arranque 1
                    'TASA A2': 29,  # Tasa de cuentas de arranque 2
                    'COND': 30,     # ?
                    'BC1': 31,      # Porcentaje de extracción de barra 1
                    'BC4': 32,      # Porcentaje de extracción de barra 4 
                    'REACTIV': 33,  # Reactividad (calculada con LIN M4)
                    }

    # -- Lectura de todos los datos
    # Si hay sólo un string, lo convierto a lista de un elemento
    if isinstance(file_names, str): file_names = [file_names]
    # Variable para guardar datos de calibración del archivo
    calibracion = []
    # Itero sobre todos los archivos
    for file_name in file_names:
        with open(file_name, 'rb') as f:
            data_raw = np.fromfile(f, dtype='float', count=-1)
        # Datos en columnas para el archivo leido
        data_cols_single = np.reshape(data_raw, (-1, 34)).T
        # La primer lectura corresponde a valores de calibración
        # TODO: cuando se sepa qué es, ver cómo usarlos
        calibracion.append(data_cols_single[:, 0])
        #  print(f"Datos de calibración:\n {calibracion}")
        # Sigo trabajando sin la calibración
        data_cols_single = data_cols_single[:, 1:]
        # Concateno los datos en columnas de todos los archivos
        try:
            data_cols = np.concatenate((data_cols, data_cols_single), axis=1)
        except UnboundLocalError:
            # Si la variable data_new no existe
            data_cols = data_cols_single

    if formato == 'datetime':
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0)
    elif formato == 'time':
        if region:
            raise ValueError(
            "La selección de datos sólo es valida con formato 'datetime'")
        to_datetime = lambda t: xlrd.xldate_as_datetime(t, 0).time()
    else:
        ValueError("'formato' no reconocido para datetime")
    # Convierto datetime del formato excell al formato datetime de python
    datetime = np.vectorize(to_datetime)(data_cols[0, :])


    # Convierto las variables que quiero leer en el índice de su columna
    if len(variables) !=0:
        sel_indx = [label_to_int[s] for s in variables]
        col_names = variables
    else:
        sel_indx = list(range(1, 34))
        col_names = label_to_int.keys()

    if panda:
        # Se devuelve un dataframe
        import pandas as pd
        df = pd.DataFrame(data_cols[sel_indx, :].T, columns=col_names)
        # Agrago columna con fecha y hora
        df.insert(0, 'Fecha-Hora', datetime)
        # Hago que la fecha y hora sea el índice del dataframe
        # df = df.set_index('Fecha-Hora')
        if region:
            zona = (df['Fecha-Hora'] >= region[0]) & \
                   (df['Fecha-Hora'] <= region[1])
            return df[zona].reset_index(drop=True)
        else:
            return df
    else:
        # Se devuelve por separado vector de Fecha-Hora y datos
        return datetime, data_cols[sel_indx, :]
