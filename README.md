#PREPROCESAMIENTO
from librerias import *
# Contraseña del archivo inventario

class Main():
    
    def __init__(self):
        print(" ")
       
    def nuevos_ingresos(self,mes, nombre_mes, periodo2):
    
        #1.INSUMO INICIALES
        ruta1=r"\\sbmdebns03\SOX\VP_SERV_ADM_SEG\DIR_ACT_FIJ_INMOBILIAR\GCIA_VALORAC_GARANT\Realizar monitoreo y actualización de valores del portafolio de BRP y restituidos\1.INSUMOS\INVENTARIO_BRP"
        ruta2=r"\\sbmdebns03\SOX\VP_SERV_ADM_SEG\DIR_ACT_FIJ_INMOBILIAR\GCIA_VALORAC_GARANT\Realizar monitoreo y actualización de valores del portafolio de BRP y restituidos\1.INSUMOS\MONITOREO_BRP"
        RutaE1=r"\\sbmdebns03\SOX\VP_SERV_ADM_SEG\DIR_ACT_FIJ_INMOBILIAR\GCIA_VALORAC_GARANT\Realizar monitoreo y actualización de valores del portafolio de BRP y restituidos\4.CONTROLES"
        RutaE2=r"\\sbmdebns03\SOX\VP_SERV_ADM_SEG\DIR_ACT_FIJ_INMOBILIAR\GCIA_VALORAC_GARANT\Realizar monitoreo y actualización de valores del portafolio de BRP y restituidos\2.SALIDAS\DELTAS"
        nombreE1='\\Control_FechaIngreso_'
        nombreE2='\\delta_'  
        extension=".xlsx"
        contrasena = 'GVG1'
            
        # Lista de insumos INVENTARIOS
        # Este insumo quedara alojado en la carpeta INVENTARIO_BRP, se debe llamar:BD Brps-Monitoreo de Avalúos-##, numero es el mes de ejecucion, es decir, si estamos en enero deberia ser BD Brps-Monitoreo de Avalúos-01
        insumo1 = [
            "\BD Brps-Monitoreo de Avalúos-01",
            "\BD Brps-Monitoreo de Avalúos-02",
            "\BD Brps-Monitoreo de Avalúos-03",
            "\BD Brps-Monitoreo de Avalúos-04",
            "\BD Brps-Monitoreo de Avalúos-05",
            "\BD Brps-Monitoreo de Avalúos-06",
            "\BD Brps-Monitoreo de Avalúos-07",
            "\BD Brps-Monitoreo de Avalúos-08",
            "\BD Brps-Monitoreo de Avalúos-09",
            "\BD Brps-Monitoreo de Avalúos-10",
            "\BD Brps-Monitoreo de Avalúos-11",
            "\BD Brps-Monitoreo de Avalúos-12"]
            # Lista de insumos MONITOREO
            #Dejar el insumo en la carperta MONITOREO_BRP, se debe llamar:Monitoreo Portafolio mmm.xlsx, el mmm es el nombre del mes-1 a la ejecucion, es decir, si estamos en enero deberia ser Monitoreo Portafolio Diciembre.xlsxinsumo2 = [
        insumo2 = [
                "\Monitoreo Portafolio Enero",
                "\Monitoreo Portafolio Febrero",
                "\Monitoreo Portafolio Marzo",
                "\Monitoreo Portafolio Abril",
                "\Monitoreo Portafolio Mayo",
                "\Monitoreo Portafolio Junio",
                "\Monitoreo Portafolio Julio",
                "\Monitoreo Portafolio Agosto",
                "\Monitoreo Portafolio Septiembre",
                "\Monitoreo Portafolio Octubre",
                "\Monitoreo Portafolio Noviembre",
                "\Monitoreo Portafolio Diciembre"]
                
            #2.FUNCIONES
            ## 1. Funcion para quitar tildes,poner en mayusculas y quitar espacios de alguna columna
        
        def quitartildes(column):
            a,b='áéíóúüñÁÉÍÓÚÜàèìòù','aeiouunAEIOUUaeiou'
            trans=str.maketrans(a,b)#transponer
            column=column.str.strip()
            column=column.str.upper()
            column=column.str.translate(trans)
            return column 

        #2. Funcion para remover caracteres especiales
        def remove_chars(s):
            return re.sub('[^0-9]+|[(+*)]', "",s)

        #3. Funcion para para CONTROL DE FECHA DE INGRESO:
        # debe tener fecha del mes anterior a la ejecucion-si la fecha de ingreso no esta dentro del rango del mes anterior generar alerta del nuevo ingreso. Pero igual se debe ingresar.
        def validar_fecha(fecha_str):
            if isinstance(fecha_str, datetime):
                return fecha_str
            else:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    return fecha
                except ValueError:
                    return None
                
        def control_fechas(df11, campos_fechas):
            fechas_problematicas = []
            for campo in campos_fechas:
                for indice, valor in df11[campo].items():
                    if pd.notna(valor):
                        fecha = validar_fecha(valor)
                        if fecha is None:
                            fechas_problematicas.append((campo, indice, valor))

            # Crear un DataFrame con las fechas problemáticas
            df_problemas = pd.DataFrame(fechas_problematicas, columns=['Campo', 'Indice', 'Valor'])
            return df_problemas
        
        #Funcion que identifica fechas por fuera de un rango de 1 mes.
        def es_fecha_valida(fecha,campo):
            mensaje = ""
            if pd.isnull(fecha) or fecha == "":
                mensaje = "No aplica: Campo vacío o nulo."
                return mensaje
            
            fecha_actual = datetime.now()
            primer_dia_mes_actual = fecha_actual.replace(day=1)
            ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
            mes_1 = fecha_actual - timedelta(days=30)
            limite_inferior = mes_1.replace(day=1)
            limite_superior = ultimo_dia_mes_anterior.replace(day=ultimo_dia_mes_anterior.day)
            
            try:
                fecha = datetime.strptime(str(fecha), "%Y-%m-%d")
                if limite_inferior <= fecha <= limite_superior:
                    mensaje = "La fecha está dentro del rango de 1 mes."
                    return mensaje
                elif fecha < limite_inferior:
                    mensaje = "La fecha está más de 1 mes en el pasado."
                    return mensaje
                else:
                    mensaje = "La fecha está más de 1 mes en el futuro."
                    return mensaje
            except ValueError:
                mensaje = "Error: Formato de fecha no válido para el campo '{}'".format(campo)
                return mensaje
                
        def adaptar_fecha(df, columna:str):
            try:
                # Verificar si el campo 'Fecha Ingreso' es de tipo datetime
                if pd.api.types.is_datetime64_any_dtype(df[columna]):
                    # Si es una fecha, quitar la zona horaria si está presente
                    if df[columna].dt.tz is not None:
                        df[columna] = df['Fecha de Ingreso'].dt.tz_convert(None)
                        print("Se quitó la zona horaria de la columna '{}'.".format(columna))

                    # Formatear la fecha como una cadena en el formato deseado
                    df[columna] = df[columna].dt.strftime('%Y-%m-%d')
                    print("La columna '{}' se formateó en el formato '%Y-%m-%d'.".format(columna))
                else:
                    # Intentar convertir el campo 'Fecha Ingreso' a datetime
                    df[columna] = pd.to_datetime(df[columna],errors='coerce',utc=True, format='%Y-%m-%d')
                    df[columna] = df[columna].dt.tz_localize(None)
                    print("Se convirtió la columna '{}' a tipo datetime y se formateó en el formato '%Y-%m-%d'.".format(columna))
            
            except Exception as e:
                # Si ocurre algún error, mostrar un mensaje de error
                print("Error:", e)
        
           
        #Diccionarios
        dic_Procedencia={'DACION':'DACION EN PAGO','DACION EN PAGO':'DACION EN PAGO','RESTITUCION JUDICIAL':'RESTITUCION','RESTITUCION':'RESTITUCION','RESTITUCION JUDICIAL':'RESTITUCION','RESTITUCION VOLUNTARIA':'RESTITUCION','ADJUDICACION':'ADJUDICACION','CESION':'CESION','OFICIO':'OFICIO','PAGO DIRECTO':'PAGO DIRECTO','RECOLOCACION':'RECOLOCACION'}

        dic_grupoActi={" APARTAMENTO":"INMUEBLES","ACCESORIOS":"MAQUINARIA Y EQUIPOS","ACCESORIOS TECNOLOGICOS":"MAQUINARIA Y EQUIPOS",
                        "ACCIONES":"ACCIONES","APARTAMENTO":"INMUEBLES","AUTOMOVIL":"VEHICULOS","BARCO":"MAQUINARIA Y EQUIPOS","BODEGA":"INMUEBLES",
                        "BUS":"VEHICULOS","BUSETA":"VEHICULOS","CAMION":"VEHICULOS","CAMIONETA":"VEHICULOS","CAMPERO":"VEHICULOS","CAMPEROS":"VEHICULOS",
                        "CASA":"INMUEBLES","COMPUTADORES":"MAQUINARIA Y EQUIPOS","CONSULTORIO":"INMUEBLES",
                        "DEPOSITO":"INMUEBLES","EDIFICIO":"INMUEBLES","ELECTRODOMESTICOS":"MAQUINARIA Y EQUIPOS",
                        "EQUIPOS DE CONFECCION":"MAQUINARIA Y EQUIPOS","EQUIPOS DE IMPRESION":"MAQUINARIA Y EQUIPOS","EQUIPOS DE PANADERIA":"MAQUINARIA Y EQUIPOS",
                        "EQUIPOS MEDICOS":"MAQUINARIA Y EQUIPOS","FIDEICOMISO":"DERECHOS FIDUCIARIOS","FIDEICOMISO":"INMUEBLES","FINCA":"INMUEBLES","GARAJE":"INMUEBLES",
                        "IMPRESORA":"MAQUINARIA Y EQUIPOS","KABAN":"MAQUINARIA Y EQUIPOS","LEUTERT":"MAQUINARIA Y EQUIPOS","LOCA - LOCAL":"INMUEBLES","LOCAL":"INMUEBLES",
                        "LOTE":"INMUEBLES","LOTE CON SERVICIOS":"INMUEBLES","LOTE INDUSTRIAL":"INMUEBLES","LOTE TERRENO":"INMUEBLES",
                        "MAQUINARIA":"MAQUINARIA Y EQUIPOS","MAQUINARIA Y EQUIPOS INDUSTRIALES":"MAQUINARIA Y EQUIPOS","MAQUINARIAY EQUIPO":"MAQUINARIA Y EQUIPOS",
                        "MAQUINARIAY EQUIPOS INDUSTRIALES":"MAQUINARIA Y EQUIPOS","MICROBUS":"VEHICULOS","MONTACARGA":"MAQUINARIA Y EQUIPOS","MOTO":"VEHICULOS","MOTOCARRO":"VEHICULOS",
                        "MUEBLES Y ENSERES":"MAQUINARIA Y EQUIPOS","OFICINA":"INMUEBLES","OTROS":"INMUEBLES","OTROS":"MAQUINARIA Y EQUIPOS","PARQUEADERO":"INMUEBLES",
                        "RETROCARGADORA":"MAQUINARIA Y EQUIPOS","RETROEXCAVADORA":"MAQUINARIA Y EQUIPOS","SOFTWARE":"MAQUINARIA Y EQUIPOS","SPARTEK SYSTEMS":"MAQUINARIA Y EQUIPOS",
                        "TERRENO":"INMUEBLES","TERRENO-LOTE":"INMUEBLES","TRACTOCAMION":"VEHICULOS","TRACTOR":"MAQUINARIA Y EQUIPOS",
                        "TRAILER":"MAQUINARIA Y EQUIPOS","UPS":"MAQUINARIA Y EQUIPOS","VANS":"VEHICULOS","VOLQUETA":"VEHICULOS","VEHICULOS":"VEHICULOS",
                        "TERRENO -  LOTE":"INMUEBLES","CONFECCIONES TEXTIL":"MAQUINARIA Y EQUIPOS","MAQUINARIA - TECNOLOGIA":"MAQUINARIA Y EQUIPOS"}

        dic_TipoActi={" APARTAMENTO":"VIVIENDA","ACCESORIOS":"MAQUINARIA Y EQUIPOS","ACCESORIOS TECNOLOGICOS":"MAQUINARIA Y EQUIPOS",
                        "ACCIONES":"ACCIONES","APARTAMENTO":"VIVIENDA","AUTOMOVIL":"VEHICULOS","BARCO":"MAQUINARIA Y EQUIPOS","BODEGA":"BODEGA","BUS":"VEHICULOS",
                        "BUSETA":"VEHICULOS","CAMION":"VEHICULOS","CAMIONETA":"VEHICULOS","CAMPERO":"VEHICULOS","CAMPEROS":"VEHICULOS","CASA":"VIVIENDA",
                        "COMPUTADORES":"MAQUINARIA Y EQUIPOS","CONSULTORIO":"OFICINA","DEPOSITO":"BODEGA","EDIFICIO":"EDIFICIO",
                        "ELECTRODOMESTICOS":"MAQUINARIA Y EQUIPOS","EQUIPOS DE CONFECCION":"MAQUINARIA Y EQUIPOS","EQUIPOS DE IMPRESION":"MAQUINARIA Y EQUIPOS","EQUIPOS DE PANADERIA":"MAQUINARIA Y EQUIPOS",
                        "EQUIPOS MEDICOS":"MAQUINARIA Y EQUIPOS","FIDEICOMISO":"DERECHOS FIDUCIARIOS","FIDEICOMISO":"LOCAL COMERCIAL","FIDEICOMISO":"LOTES Y FINCAS","FIDEICOMISO":"VIVIENDA",
                        "FINCA":"LOTES Y FINCAS","GARAJE":"OFICINA","GARAJE":"VIVIENDA","IMPRESORA":"MAQUINARIA Y EQUIPOS","KABAN":"MAQUINARIA Y EQUIPOS",
                        "LEUTERT":"MAQUINARIA Y EQUIPOS","LOCA - LOCAL":"LOCAL COMERCIAL","LOCAL":"LOCAL COMERCIAL","LOTE":"LOCAL COMERCIAL","LOTE":"LOTES Y FINCAS",
                        "LOTE CON SERVICIOS":"LOTES Y FINCAS","LOTE INDUSTRIAL":"LOTES Y FINCAS","LOTE TERRENO":"LOTES Y FINCAS","MAQUINARIA":"MAQUINARIA Y EQUIPOS",
                        "MAQUINARIA Y EQUIPOS INDUSTRIALES":"MAQUINARIA Y EQUIPOS","MAQUINARIAY EQUIPO":"MAQUINARIA Y EQUIPOS","MAQUINARIAY EQUIPOS INDUSTRIALES":"MAQUINARIA Y EQUIPOS","MICROBUS":"VEHICULOS",
                        "MONTACARGA":"MAQUINARIA Y EQUIPOS","MOTO":"VEHICULOS","MOTOCARRO":"VEHICULOS","MUEBLES Y ENSERES":"MAQUINARIA Y EQUIPOS","OFICINA":"LOCAL COMERCIAL",
                        "OFICINA":"OFICINA","OTROS":"LOTES Y FINCAS","OTROS":"MAQUINARIA Y EQUIPOS","PARQUEADERO":"VIVIENDA","RETROCARGADORA":"MAQUINARIA Y EQUIPOS",
                        "RETROEXCAVADORA":"MAQUINARIA Y EQUIPOS","SOFTWARE":"MAQUINARIA Y EQUIPOS","SPARTEK SYSTEMS":"MAQUINARIA Y EQUIPOS","TERRENO":"LOTES Y FINCAS","TERRENO-LOTE":"LOTES Y FINCAS","TRACTOCAMION":"VEHICULOS",
                        "TRACTOR":"MAQUINARIA Y EQUIPOS","TRAILER":"MAQUINARIA Y EQUIPOS","UPS":"MAQUINARIA Y EQUIPOS","VANS":"VEHICULOS","VOLQUETA":"VEHICULOS","VEHICULOS":"VEHICULOS","TERRENO -  LOTE":"LOTES Y FINCAS","CONFECCIONES TEXTIL":"MAQUINARIA Y EQUIPOS",
                        "MAQUINARIA - TECNOLOGIA":"MAQUINARIA Y EQUIPOS"}
                        
        #Seleccionando insumos
        # Patrón de expresión regular para buscar insumos
        patron = re.compile(fr"\\BD Brps-Monitoreo de Avalúos-{mes}$")
        patron2 = re.compile(fr"\\Monitoreo Portafolio {nombre_mes}$")

        # Filtrar insumos que coincidan con el patrón
        insumo_seleccionado = next((insumo for insumo in insumo1 if patron.match(insumo)), None)
        insumo_seleccionado2 = next((insumo2 for insumo2 in insumo2 if patron2.match(insumo2)), None)

        # Imprimir los insumos seleccionados
        print("Insumos seleccionado:", insumo_seleccionado,",", insumo_seleccionado2)

        #Creacion de los df
        rutaf1=ruta1+str(insumo_seleccionado)+extension
        rutaf2=ruta2+str(insumo_seleccionado2)+extension
        #inventario
        try:
            # Crear una instancia de Excel
            xlapp = win32com.client.Dispatch("Excel.Application")
            xlwb = xlapp.Workbooks.Open(rutaf1, False, True, None, contrasena)
            # Seleccionar la hoja llamada "Monitoreo Avalúos"
            sheet_name = 'Monitoreo Avalúos'
            xlsheet = xlwb.Sheets(sheet_name)
            # Obtener los datos desde la tercera fila y las columnas de la 2 a la 42
            data = xlsheet.Range(xlsheet.Cells(3, 2), xlsheet.Cells(xlsheet.UsedRange.Rows.Count, 42)).Value
            # Crear un DataFrame con los datos y considerar la tercera fila como encabezado
            df1 = pd.DataFrame(data[1:], columns=data[0])
            # Cerrar el libro de trabajo sin guardar cambios
            xlwb.Close(False)
            # Cerrar la instancia de Excel
            xlapp.Quit()
            print("Archivo Excel de Inventario cargado y DataFrame1 creado exitosamente.")
        except Exception as e:
            print(f"No se pudo abrir el archivo Excel de Inventario que esta protegido. Error: {e}")
            
        #Monitoreo INGRESOS VA
        try:
            df2= pd.read_excel(rutaf2,"Ingresos VA")
            print("Archivo Excel de Monitoreo-Ingresos cargado y DataFrame2 creado exitosamente.")
        except Exception as e:
            print(f"No se pudo abrir el archivo Excel de monitoreo. Error: {e}")
            
        #Monitoreo Actualizaciones
        try:
            df3= pd.read_excel(rutaf2,"Actualizaciones",header=3)# Se usa header=3 ya que el índice de las filas empieza en 0
            # Encuentra el índice de la última fila no vacía
            ultima_fila = df3.index[df3.isnull().all(axis=1)].min()
            df3 = df3.iloc[:ultima_fila]
            print("Archivo Excel de Monitoreo-Actualizaciones cargado y DataFrame3 creado exitosamente.")
        except Exception as e:
            print(f"No se pudo abrir el archivo Excel de Monitoreo-Actualizaciones . Error: {e}")

        #Quitar espacios de las columnas
        df3.rename(columns=lambda x: x.strip(), inplace=True)
        df2.rename(columns=lambda x: x.strip(), inplace=True)
        # Eliminar registros con NaN en la columna "inventario"
        df2 = df2.dropna(subset=['Inventario'])
        df3 = df3.dropna(subset=['Codigo BRP'])
        df1 = df1.dropna(subset=['Número de inventario o placa'])

        #Cantidad de registros
        print("Número de registros en el DataFrame 1(Inventario):", df1.shape[0])
        print("Número de registros en el DataFrame 2(Monitoreo):", df2.shape[0])
        print("Número de registros en el DataFrame 2(Monitoreo):", df3.shape[0])
        
        #Creando el campo FechaIngresoBD
        df1['Fecha_ingresoBD']=periodo2
        #creando df inventario
        #SELECCIONANDO CAMPOS DEL INSUMO INVENTARIO
        #inventario
        df11=df1.copy()
        df11=df11[['Número de inventario o placa','Denominación o descripción del activo fijo','NIT','Descripción','Ubicación','Dirección','Procedencia','Estado del bien','Descripción clase activo fijo','% PARTICIP','Fecha de capitalización','Costo del BRP (COLGAAP)','Valor Avalúo','Saldo IFRS','Precio de Lista','Fecha Valor Avalúo','Fecha_ingresoBD','Fecha referencia','Valor referencia']]
        #renombrando
        df11 = df11.rename(columns={"Número de inventario o placa":"Inventario",
                                    "Denominación o descripción del activo fijo":"Descripcion_Activo_Fijo",
                                    "NIT":"NIT",
                                    "Descripción":"Nombre/Razon_Social",
                                    "Ubicación":"Ubicacion",
                                    "Dirección":"Direccion",
                                    "Procedencia":"Procedencia",
                                    "Estado del bien":"Estado_del_bien",
                                    "Descripción clase activo fijo":"Descripcion_clase_activo_fijo",
                                    "% PARTICIP":"Participación",
                                    "Fecha de capitalización":"Fecha de Ingreso",
                                    "Costo del BRP (COLGAAP)":"Valor Admisible",
                                    "Valor Avalúo":"Valor Avaluo",
                                    "Precio de Lista":"Precio_Asignado",
                                    "Fecha Valor Avalúo":"Fecha Avaluo"})

        df11.info()
        #Cambiando tipologias a los campos
        campos_con_error = []

        try:
            df11['Inventario'] = df11['Inventario'].astype(int)
            print("Inventario: Valores convertidos correctamente")
        except Exception as e:
            campos_con_error.append('Inventario')
            print(f"Inventario: Valores no convertidos. Error: {e}")

        try:
            df11['NIT'] = df11['NIT'].astype(float)
            print("NIT: Valores convertidos correctamente")
        except Exception as e:
            campos_con_error.append('NIT')
            print(f"NIT: Valores no convertidos. Error: {e}")

        print("Campos con error:", campos_con_error)
        #Convirtiendo los campos de Fecha del insumo inventario en Datetime 
        Fechas_revisar=['Fecha referencia','Fecha Avaluo','Fecha de Ingreso']
        for columna in Fechas_revisar:
            print("Para la columna '{}' Se realizo:".format(columna))
            adaptar_fecha(df11, columna)
            print('\n')
        #Creando el campo llave_concatenado de #inventario+fecha de ingreso a la base
        df11['LlaveBD']=df11['Inventario'].astype(str)+"-"+df11['Fecha_ingresoBD']
        #concatenando los campos Fecha referencia Y Fecha Avaluo,Valor Avaluo Y Valor referencia, para que quede solo Fecha Avaluo,Valor Avaluo y tipologia
        df11['Fecha Avaluo1']=np.where(df11['Fecha referencia'].isna(),df11['Fecha Avaluo'],
                                    np.where(df11['Fecha Avaluo']>=df11['Fecha referencia'],df11['Fecha Avaluo'],df11['Fecha referencia']))
        df11['Valor Avaluo1']=np.where(df11['Fecha referencia'].isna(),df11['Valor Avaluo'],
                                    np.where(df11['Fecha Avaluo']>=df11['Fecha referencia'],df11['Valor Avaluo'],df11['Valor referencia']))
        df11['Tipo de Valoración']=np.where(df11['Fecha referencia'].isna(),'AVALÚO CON VISITA',
                                            np.where(df11['Fecha Avaluo']>=df11['Fecha referencia'],'AVALÚO CON VISITA','AVALÚO POR REFERENCIA'))
        #me muestre la cantidad de nulos 
        # Identificar valores nulos
        nulos = df11.isna().sum()
        # Identificar espacios en columnas de tipo string
        espacios = (df11.applymap(lambda x: isinstance(x, str) and x.isspace())).sum()
        # Mostrar resultados
        print("Valores nulos por columna:")
        print(nulos)
        print("\nEspacios por columna:")
        print(espacios)
        #Completando valores nulos en el concatenado
        columnas_nulas=['Valor Admisible','Valor Avaluo','Saldo IFRS',"Valor referencia"]
        for columna in columnas_nulas:
            df11[columna].replace(" ", np.nan, inplace=True)

        #Reemplazando valores de campos por los diccionarios
        df11["Procedencia"]=quitartildes(df11["Procedencia"]).replace(dic_Procedencia)
        df11["Descripcion_Activo_Fijo"]=quitartildes(df11["Descripcion_Activo_Fijo"])
        df11["Nombre/Razon_Social"]=quitartildes(df11["Nombre/Razon_Social"])
        df11["Ubicacion"]=quitartildes(df11["Ubicacion"])
        df11["Direccion"]=quitartildes(df11["Direccion"])
        df11["Estado_del_bien"]=quitartildes(df11["Estado_del_bien"])
        df11["Descripcion_clase_activo_fijo"]=quitartildes(df11["Descripcion_clase_activo_fijo"])
        df11["Valor Admisible"]=df11["Valor Admisible"].fillna(0)
        df11["Valor Avaluo"]=df11["Valor Avaluo"].fillna(0)
        df11["Saldo IFRS"]=df11["Saldo IFRS"].fillna(0)
        df11["Precio_Asignado"]=df11["Precio_Asignado"].fillna(0)
        df11["Valor referencia"]=df11["Valor referencia"].fillna(0)
        
        #Extrayendo informacion de monitoreo
        #Seleccionando campos de monitoreo
        #Ingresos
        df21=df2.copy()
        df21=df21[['Inventario','Matricula','Valor Admisible GVGA','Perito','Rotación','Endeudamiento']]
        df21 = df21.rename(columns={"Inventario":"Inventario_monitoreo",
                                    "Matricula":"Placa_Matricula",
                                    "Valor Admisible GVGA":"Valor Admisible GVGA",
                                    "Perito":"Perito_Avaluo_inicial",
                                    "Rotación":"Tiempo de Rotación Asignado",
                                    "Endeudamiento":"Endeudamiento"})

        #Actualizaciones
        df31=df3.copy()
        df31=df31[['Codigo BRP','Fecha actualizacion','Valor Avalúo Actualizado','Tipo de Valoración','Perito','Observaciones']]
        df31 = df31.rename(columns={"Codigo BRP":"Inventario",
                                    "Fecha actualizacion":"Fecha Avaluo_Act",
                                    "Valor Avalúo Actualizado":"Valor Avaluo_Act",
                                    'Tipo de Valoración':'Tipo de Valoración_Act'})
        
        #Realizando cruce de inventarios y monitoreo
        #casteando todas las llaves a entero
        df11['Inventario'] = df11['Inventario'].astype(int)
        df21['Inventario_monitoreo'] = df21['Inventario_monitoreo'].astype(int)
        df31['Inventario'] = df31['Inventario'].astype(int)
        #Concatenando insumos en una sola base: Inventario y monitoreo-Ingresos
        df_conca1 = pd.merge(df11,df21,how='left',left_on='Inventario',right_on='Inventario_monitoreo')
        #cascada de cruce
        print(df_conca1[['Inventario','Inventario_monitoreo']].count())
        #Concatenando insumos en una sola base: Inventario y monitoreo-Actualizacion
        df_conca = pd.merge(df_conca1,df31,how='left',on='Inventario',indicator=True)
        #VALIDACION DE LOS ACTIVOS QUE SE ACTUALIZACION EN EL PAQUETE DE MONITOREO
        #Revisando el merge: los que estan maracadas como both son los ingresos que se activaron para su actualizacion
        #son los que se deben hacer la validacion de la coincidencia de los campos fecha avaluo, valor avaluo, perito y tipologia de valoracion
        print(df_conca['_merge'].value_counts())

        #Separando los activos que tuvieron actualizacion para hacer compartivo de los valores y fechas de avaluos
        df_conca_actu=df_conca[df_conca['_merge']=='both']
        df_conca_2=df_conca[df_conca['_merge']!='both']
        print(' ')
        print('La dimension de la base de activos Actualizados es: ',df_conca_actu.shape)
        print('La dimension de la base de activos sin Actualizar es: ',df_conca_2.shape)

        #Homologando el campo tipo de Valoración_Act para que coincida
        df_conca_actu['Tipo de Valoración_Act']=df_conca_actu['Tipo de Valoración_Act'].str.upper()
        df_conca_actu['Tipo de Valoración_Act2']=np.where(df_conca_actu['Tipo de Valoración_Act']=='AVALÚO CON VISITA','AVALÚO CON VISITA','AVALÚO POR REFERENCIA')

        #En los campos Fecha avaluo, Valor avaluo y Tipologia siempre prima la que se encuentre en el archivo de monitoreo hoja actualizaciones
        df_conca_actu['Val_Fecha avaluo']=np.where(df_conca_actu['Fecha Avaluo1']==df_conca_actu['Fecha Avaluo_Act'],'OK','NO COINCIDE LAS FECHAS DE LOS AVALÚOS')
        df_conca_actu['Val_Valor avaluo']=np.where(df_conca_actu['Valor Avaluo1']==df_conca_actu['Valor Avaluo_Act'],'OK','NO COINCIDE LOS VALORES DE LOS AVALÚOS')
        df_conca_actu['Val_Tipologia']=np.where(df_conca_actu['Tipo de Valoración']==df_conca_actu['Tipo de Valoración_Act2'],'OK','NO COINCIDE LA TIPOLOGIA DE LOS AVALÚOS')

        #Creando Valor Avaluo3, Fecha Avaluo3 y tipologia3, siempre prima el de moniotreo
        df_conca_actu['Valor Avaluo3']=np.where(df_conca_actu['Val_Valor avaluo']=='OK',df_conca_actu['Valor Avaluo1'],df_conca_actu['Valor Avaluo_Act'])
        df_conca_actu['Fecha Avaluo3']=np.where(df_conca_actu['Val_Fecha avaluo']=='OK',df_conca_actu['Fecha Avaluo1'],df_conca_actu['Fecha Avaluo_Act'])
        df_conca_actu['Fecha Avaluo3'] = pd.to_datetime(df_conca_actu['Fecha Avaluo3'], unit='ns')
        df_conca_actu['Tipo de Valoración3']=np.where(df_conca_actu['Val_Tipologia']=='OK',df_conca_actu['Tipo de Valoración_Act'],df_conca_actu['Tipo de Valoración'])

        #Seleccionar los campos finales del df_conca_actu
        Columnasfinales=['Inventario','Inventario_monitoreo', 'Descripcion_Activo_Fijo', 'NIT', 'Nombre/Razon_Social','Ubicacion', 'Direccion', 'Procedencia', 'Estado_del_bien',
                        'Descripcion_clase_activo_fijo', 'Participación', 'Fecha de Ingreso','Valor Admisible', 'Saldo IFRS', 'Precio_Asignado',
                        'Fecha Avaluo3','Valor Avaluo3','Tipo de Valoración3', 'Fecha_ingresoBD','LlaveBD', 'Placa_Matricula','Valor Admisible GVGA', 'Perito_Avaluo_inicial',
                        'Tiempo de Rotación Asignado', 'Endeudamiento', 'Perito', 'Observaciones']
        df_conca_actu2=df_conca_actu[Columnasfinales]
        df_conca_actu2 = df_conca_actu2.rename(columns={'Fecha Avaluo3':'Fecha Avaluo',
                                                        'Valor Avaluo3':'Valor Avaluo',
                                                        'Tipo de Valoración3':'Tipo de Valoración'})

        #Seleccionar los campos finales del df_conca_2
        Columnasfinales2=['Inventario','Inventario_monitoreo', 'Descripcion_Activo_Fijo', 'NIT', 'Nombre/Razon_Social','Ubicacion', 'Direccion', 'Procedencia', 'Estado_del_bien',
                        'Descripcion_clase_activo_fijo', 'Participación', 'Fecha de Ingreso','Valor Admisible', 'Saldo IFRS', 'Precio_Asignado',
                        'Fecha Avaluo1','Valor Avaluo1','Tipo de Valoración', 'Fecha_ingresoBD','LlaveBD', 'Placa_Matricula','Valor Admisible GVGA', 'Perito_Avaluo_inicial',
                        'Tiempo de Rotación Asignado', 'Endeudamiento', 'Perito', 'Observaciones']
        df_conca_3=df_conca_2[Columnasfinales2]
        df_conca_3 = df_conca_3.rename(columns={'Fecha Avaluo1':'Fecha Avaluo',
                                                        'Valor Avaluo1':'Valor Avaluo'})

        #concateno ambas bases
        df_concaFinal= pd.concat([df_conca_actu2, df_conca_3], ignore_index=True)
        
        #Creando campo Estado:Ingresos y En existencia
        df_concaFinal['Estado'] = np.where(pd.isna(df_concaFinal['Inventario_monitoreo']),'EN EXISTENCIA','INGRESOS')

        #Informacion final
        valores_estado=df_concaFinal['Estado'].value_counts()
        total=df_concaFinal.shape[0]
        # Extraer los valores individuales
        existencia_count = valores_estado.get('EN EXISTENCIA', 0)
        ingresos_count = valores_estado.get('INGRESOS', 0)
        print("Se registran {} Activos totales, de los cuales se tienen {} en Existencia y {} Ingresos".format(
            total, existencia_count, ingresos_count))
        
        #Seleccionando campos finales
        Columnas_dfexportar=['Inventario', 'Descripcion_Activo_Fijo', 'NIT','Nombre/Razon_Social', 'Ubicacion', 'Direccion', 'Procedencia',
                                    'Estado_del_bien', 'Descripcion_clase_activo_fijo', 'Participación','Fecha de Ingreso', 'Valor Admisible', 'Saldo IFRS',
                                    'Precio_Asignado', 'Fecha Avaluo','Valor Avaluo', 'Tipo de Valoración','Fecha_ingresoBD','LlaveBD', 'Placa_Matricula', 'Valor Admisible GVGA',
                                    'Perito_Avaluo_inicial', 'Tiempo de Rotación Asignado','Endeudamiento', 'Perito', 'Observaciones', 'Estado']
        df_concaFinal2=df_concaFinal[Columnas_dfexportar]
        
        # Identificar valores nulos
        nulos = df_concaFinal2.isna().sum()
        # Identificar espacios en columnas de tipo string
        espacios = (df_concaFinal2.applymap(lambda x: isinstance(x, str) and x.isspace())).sum()
        # Mostrar resultados
        print("Valores nulos por columna:")
        print(nulos)
        print("\nEspacios por columna:")
        print(espacios)
        
        #IMPUTANDO NULOS
        #Completando valores nulos en el concatenado
        columnas_nulas=['Placa_Matricula','Valor Admisible GVGA','Perito_Avaluo_inicial','Tiempo de Rotación Asignado','Endeudamiento','Perito']
        for columna in columnas_nulas:
            df_concaFinal2[columna].replace(" ", np.nan, inplace=True)

        df_concaFinal2["Placa_Matricula"]=quitartildes(df_concaFinal2["Placa_Matricula"].fillna("SIN INFORMACION"))
        df_concaFinal2["Perito"]=quitartildes(df_concaFinal2["Perito"].fillna("SIN INFORMACION"))
        df_concaFinal2["Perito_Avaluo_inicial"]=quitartildes(df_concaFinal2["Perito_Avaluo_inicial"].fillna("SIN INFORMACION"))
        df_concaFinal2["Valor Admisible GVGA"]=df_concaFinal2["Valor Admisible GVGA"].fillna(0)
        df_concaFinal2["Tiempo de Rotación Asignado"]=df_concaFinal2["Tiempo de Rotación Asignado"].fillna(0)
        df_concaFinal2["Endeudamiento"]=df_concaFinal2["Endeudamiento"].fillna(0)
        
        #CREANDO CONTROLES
        #control de no coincidencias pegandome de df_conca_actu
        df_control_coinci=df_conca_actu[['Inventario','Val_Fecha avaluo','Val_Valor avaluo', 'Val_Tipologia','Fecha referencia','Valor referencia','Fecha Avaluo','Valor Avaluo']]
        #control de fechas
        #Validando formato de fechas
        Campos_fechas={"Fecha de Ingreso","Fecha Avaluo1"}
        df_fechas_problematicas = control_fechas(df11, Campos_fechas)

        #validando rango de fechas, debe ser inferior a 1 mes
        # Iterar sobre cada fila del DataFrame
        # Definir una lista para almacenar los resultados
        resultados = []

        for indice, fila in df11.iterrows():
            fecha = fila['Fecha de Ingreso']
            comentario = es_fecha_valida(fecha, 'Fecha de Ingreso')  # Llamar a la función es_fecha_valida
            resultados.append({'Fecha': fecha, 'Comentario': comentario})

        # Convertir la lista de resultados en un nuevo DataFrame
        df_resultados = pd.DataFrame(resultados)

        # Mostrar el DataFrame resultante
        print(df_resultados)

        # Eliminar duplicados basados en la columna 'Campo'
        df_resultado_sin_duplicados = df_resultados.drop_duplicates()  

        #Control del campo endeudamiento
        # Mostrar los datos con separadores por coma y punto
        try:
            # Convertir los datos del campo 'Endeudamiento' a tipo string
            df21['Endeudamiento'] = df21['Endeudamiento'].astype(str)
            
            # Verificar si el campo 'Endeudamiento' contiene comas o puntos
            df_coma = df21[df21['Endeudamiento'].str.contains('[,]', na=False)]
            
            if not df_coma.empty:
                print("Datos monetarios con separadores diligenciados manualmente:")
                print(df_coma)
            else:
                mensaje = "No se encontraron valores de endeudamiento con separadores manuales."
                print(mensaje)
        except ValueError:
            mensaje = "La base de monitoreo no contiene valores de endeudamiento incorrectos"
            print(mensaje)
            
        #Creando control de grupo de activo y tipo de activo
        # Extrae las llaves del diccionario grupo activo y tipo activo, tener en cuenta que para hacer la creacion de estos dos campos se utiliza las mismas llaves cambian son los valores de homologacion
        llaves_diccionario = list(dic_grupoActi.keys())
        # Extrae los valores únicos de la columna Descripcion_Activo_Fijo
        valores_activo = set(df11['Descripcion_Activo_Fijo'])
        # Encuentra los valores que están en el DataFrame pero no en el diccionario
        valores_faltantes = [valor for valor in valores_activo if valor not in llaves_diccionario]

        #Creando df para el control
        df_grupoact= pd.DataFrame({
            'Campo': valores_faltantes,
            'Alerta': 'Campo no encontrado en el diccionario'})
        # Si hay valores faltantes, muestra una alerta
        if valores_faltantes:
            print("Alerta: Los siguientes valores no se encuentran en el diccionario:")
            for valor in valores_faltantes:
                print("-", valor)
        else:
            print("Todos los valores del DataFrame están presentes en el diccionario.")    
            
        # Revision de controles que salieron para revisar en el mes de ejecución
        dataframes = [df_fechas_problematicas, df_resultado_sin_duplicados, df_coma, df_grupoact, df_control_coinci]
        nombres_sheets = ["fechasinvalidas", "Rangofechas", "ValorEndeudamiento", "CatalogoGrupoactivo", "Coincidencia_InvenVsMonit"]

        print("CONTROLES A REVISAR DEL PERIODO {}:\n".format(periodo2))
        for df, nombre_sheet in zip(dataframes, nombres_sheets):
            if df.shape[0] != 0:
                print("El archivo '{}' en la hoja '{}' tiene {} registro(s) para revisar.\n".format(nombreE1+periodo2, nombre_sheet, df.shape[0]))    
            
        #EXPORTANDO INFORMACION
        #EXPORTANDO CONTROL
        #creando nombres automaticos
        almacenamiento=RutaE1+nombreE1+periodo2+extension
        writer = pd.ExcelWriter(almacenamiento, engine='xlsxwriter')
        df_fechas_problematicas.to_excel(writer,sheet_name="fechasinvalidas",index=False)
        df_resultado_sin_duplicados.to_excel(writer,sheet_name="Rangofechas",index=False)
        df_coma.to_excel(writer,sheet_name="ValorEndeudamiento",index=False)
        df_grupoact.to_excel(writer,sheet_name="CatalogoGrupoactivo",index=False)
        df_control_coinci.to_excel(writer,sheet_name="Coincidencia_InvenVsMonit",index=False)
        writer.save()
        writer.close()  
        
        #EXPORTANDO NUEVOS INGRESOS
        almacenamiento2=RutaE2+nombreE2+periodo2+extension
        writer = pd.ExcelWriter(almacenamiento2, engine='xlsxwriter')
        df_concaFinal2.to_excel(writer,index=False)
        writer.save()
        writer.close()

    def consolidado(self):
        print('En proceso')

    #PONER MODELOS

    #PROBANDO MODELO EN LA DATA PARA SUBIR A LA COMPETENCIA
    dataTesting['State'] = quitartildes(dataTesting['State'])
    dataTesting['Model'] = quitartildes(dataTesting['Model'])
    dataTesting['Make'] = quitartildes(dataTesting['Make'])
    dataTesting['Car_Age'] = current_year - dataTesting['Year']
    dataTesting['Mileage_Year'] = dataTesting['Year'] / dataTesting['Mileage']
    dataTesting['Brand_Model'] = dataTesting['Make'] + '_' + dataTesting['Model']
    
    X_testcru = pipeline.transform(dataTesting)
    y_predmodelo1 = xgboost_model.predict(X_testcru)
    print(y_predmodelo1[:5]) 
    df = pd.DataFrame(y_predmodelo1) 
    # Rename the default column (likely '0') to 'Price'
    df = df.rename(columns={0: 'Price'}) 
    # Save to CSV 
    df.to_csv(r"C:\Users\anasoto\Downloads\modeloxgboost9.csv", index_label='ID') 
