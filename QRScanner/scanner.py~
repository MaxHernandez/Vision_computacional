import cv, cv2
from numpy import *
from sys import exit
from time import time
from math import ceil, fabs, atan2, degrees, sqrt


def restar(izquierda, derecha, mask = 'sobel5', umbralEsquinas = 10, umbralAngulos = 10, bias_color = 30.0, gx = None, gy = None, original_thumbnail = None):
    """restar (izquierda, derecha, ...) Esta funcion sirve para restar los valores de derecha a  izquierda pixel por pixel
    por lo tanto las dos matrices de las imagenes deberian ser de la misma ancho y largo y el mismo tipo de valores
    """
    imatI = cv.GetMat(izquierda)
    imatD = cv.GetMat(derecha)
    gx = cv.GetMat(gx)
    gy = cv.GetMat(gy)
    max_value = 0
    votos = dict()
    votos_cords = dict()
    for y in range(izquierda.height):
        for x in range(izquierda.width):
            value = imatI[y, x]
            value -= imatD[y, x]
            imatD[y, x] = value
            if value > max_value:
                max_value = value

    # El vaor razon y max_value se utilizan para llevar el rango de valores a 0-255
    if max_value > 0:
        razon = 255.0 / max_value
    else:
        razon = 0.0

    ############################################################
    # En esta parte se utiliza los valores de gradientes en X y
    # Y para buscar caracteristicas que compartan las esquinas
    # y descartar algunas, esto con la finalidad de reducir el
    # ruido que se produce en etapas futuras.
    ############################################################
    for y in range(izquierda.height):
        for x in range(izquierda.width):
            value = int(imatD[y, x]*razon)
            if  value > umbralEsquinas:
                suma = gx[y, x] + gy[y, x]
                suma = (int(suma)/15)*15
                if suma in votos:
                    votos[suma] += 1
                    votos_cords[suma].append((y, x))
                else:
                    votos[suma] = 1
                    votos_cords[suma] = list()
                    votos_cords[suma].append((y, x))
            else:
                imatD[y, x] = 0

    values = votos.values()
    values.sort()

    imatO = cv.GetMat(original_thumbnail)

    ###############################################################
    # En este punto se eliminan las esquinas que tuvieron 
    # menos votos, puesto que al parecer una de las caracteristicas
    # del QR code es que son muy caoticas y tienen a no agruparse.
    ###############################################################

    corners = list()
    for i in votos.keys():
        if votos[i] < umbralAngulos: #original
            for cord in votos_cords[i]:
                if imatD[cord] > 10:
                    imatD[cord] = 255
                    corners.append(cord)
                else:
                    imatD[cord] = 0
        else:
            for cord in votos_cords[i]:
                imatD[cord] = 0
    return corners

def dfs(image, size, inicio):
    """ dfs(image, size, inicio) Esta funcion es utilizada para buscar los valores mayores y menores tanto en x como en y, obteniendo estos valores obtenemos las cordenadas de un rectangulo que rodea la mancha"""
    siguientes = list()
    siguientes.append(inicio)

    rect = [inicio[0], inicio[1], 0, 0] #Esta es la variable que guarda los valores del rectangulo que rodea la figura
    area = 0

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
        area += 1
        image[tuple(actual)] = 0

        # Estos if nos sirven para guardar los valores minimos o maximos encontrados para cada X o Y
        if actual[0] < rect[0]:
            rect[0] = actual[0]
        if actual[0] > rect[2]:
            rect[2] = actual[0]
        if actual[1] < rect[1]:
            rect[1] = actual[1]
        if actual[1] > rect[3]:
            rect[3] = actual[1]

        # Esta parte solo sirve para buscar vecinos por vicitar en el pixel actual
        for l in range(int(actual[0])-1, int(actual[0])+2):
            for h in range(int(actual[1])-1, int(actual[1])+2):
                if h >= 0 and l >= 0 and l < size[0] and h < size[1]:
                    if image[l, h] == 255:
                        if not (l, h) in siguientes:
                            siguientes.append((l, h))
    return area, rect

def find_squares(image):
    """ find_squares(image) esta funcion se encarga de buscar todas las manchas y agruparlas en diferentes listas usando como apoyo la funcion dfs() que se encuentra en este mismo codigo"""
    rects = list()
    size = (image.height, image.width)
    
    imat = cv.GetMat(image)
    ###################################################
    # Esta parte del codigo se encarga de buscar todas
    # las manchas blancas posibles y guardar cada una 
    # en diferentes ademas de calcular su area.
    # apoyandose de la funcion dfs() ademas obtiene el
    # rectangulo que rodea el area.
    ###################################################
    for y in range(size[0]):
        for x in range(size[1]):
            if imat[y, x] == 255:
                area, rect = dfs(imat, size, (y, x))
                area_aprox = (rect[2]-rect[0])*(rect[3]-rect[1])
                if area_aprox > 0:
                    filled_area = float(area) / area_aprox
                else:
                    filled_area = 0.0
                rects.append(rect)

    return rects 

def calculate_resize(actual_size, input_size):
    """ calculate_resize(actual_size, input_size) esta funcion recibe el tamano acutal de la imagen y calcula usando input_size = (nx, ny) como guia el resultado es que la nueva imagen solo no puede sobrepasar en X o en Y los valores de input_size"""
    max_actual = max(actual_size)
    max_input = max(input_size)
    rate_change = float(max_input) / max_actual
    return tuple([int(i*rate_change) for i in actual_size])

def detection(frame, size = (128, 128)):
    """detection(frame, size = (128, 128)) Esta es la funcion principal del programa, recibe como parametro el frame actual de la camara y llamando a todas las demas funciones de este codigo y apoyandose de mas funciones de opencv para llevar a cabo sus procesos, cualquier agregado normalmente se tendra que agregar aqui.
    """

#   Crear un thumbnail del frame
    image = frame
    frames = [frame]

    size_frame = cv.GetSize(image)
    size_thumbnail = calculate_resize(size_frame, size)
    thumbnail = cv.CreateImage(size_thumbnail , frame.depth, frame.nChannels)
    cv.Resize(frame, thumbnail)
    image = thumbnail
    original_thumbnail = cv.CloneImage(image)

#   Convertir a escala de grises
    size_thumbnail = cv.GetSize(thumbnail)
    grayscale = cv.CreateImage(size_thumbnail, 8, 1)
    cv.CvtColor(thumbnail, grayscale, cv.CV_RGB2GRAY)
    image = grayscale

#   Gaussian blur
#    cv.Smooth(image, image, cv.CV_MEDIAN, 3, 3)

#    Encontrar los gradientes en horizontal y vertical
    ddepth = cv.CV_16S
    gradientx = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
    gradienty = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
    cv.Sobel(grayscale, gradientx, 1, 0)
    cv.Sobel(grayscale, gradienty, 0, 1)

#   Gaussian blur
    original_grayscale = cv.CloneImage(image)
    cv.Smooth(image, image, cv.CV_MEDIAN, 3, 3)
    restar(original_grayscale, image, umbralEsquinas = 5.0, umbralAngulos = 15, gx = gradientx, gy = gradienty, original_thumbnail = original_thumbnail)

#    Make borders or points bigger
    cv.Smooth(image, image, cv.CV_BLUR, 26, 26)
    cv.Threshold(image, image, 10, 255, cv2.THRESH_BINARY)

#    Crear un cuadrado que rode todos los puntos que recibe
#    cv.BoundingRect([(1,2), (100, 190), (203, 99), (102, 202)])

#    Aumentar contraste utilizando histogramas
#    equ = cv2.equalizeHist(asmatrix(cv.GetMat(image)))
#    res = hstack((asmatrix(cv.GetMat(grayscale)), equ))
#    grayscale = cv.fromarray(equ)

    ##################################
    # Mis procesos van aqui

    original_image = cv.CloneImage(image)

    # Se calculan los cuadrados que rodean a las manchas
    rects = find_squares(image)

    image = original_image
    # razon nos servira para mapear las pociones de los cuadrados en la imagen original, recordando que la imagen con la que trabajamos es un thumbnail de la original
    razon = (float(size_frame[0]/size_thumbnail[0]), float(size_frame[1]/size_thumbnail[1]))
    frames.append(image)

    for i in rects:
        if i[1] == i[3] or i[0] == i[2]:
            continue
        
        # Se mapean los valores del thumnail a la imagen original
        pt1 = (int(i[1]*razon[0]), int(i[0]*razon[1])) 
        pt2 = (int(i[3]*razon[0]), int(i[2]*razon[1]))
        rect = (pt1[0], pt1[1], pt2[0]-pt1[0], pt2[1]-pt1[1]) # el cuadrado que rodea las manchas
        cv.Rectangle(frame, pt1, pt2, (0,255,0), thickness=1, lineType=8, shift=0) # se dibuja el cuadrado en el frame original

        # Este grupo de metodos hacen un crop en el frame original al cuadrado obtenido
        cv.SetImageROI(frame, rect);
        tmp = cv.CreateImage(cv.GetSize(frame), frame.depth, frame.nChannels)
        cv.Copy(frame, tmp)
        cv.ResetImageROI(frame)
                
        # Se vuelve a redimensionar la imagen a una imagen thumbnail
        size_thumbnail = calculate_resize(cv.GetSize(tmp), size)
        thumbnail = cv.CreateImage(size_thumbnail , tmp.depth, tmp.nChannels)
        cv.Resize(tmp, thumbnail)
        
        thumbnail_copy = cv.CloneImage(thumbnail)

        # Se convierte a escala de grises
        grayscale = cv.CreateImage(size_thumbnail, 8, 1)
        cv.CvtColor(thumbnail, grayscale, cv.CV_RGB2GRAY)

        # Este grupo de metodos aumentan el contraste utilizando para ello histogramas
        equ = cv2.equalizeHist(asmatrix(cv.GetMat(grayscale)))
        res = hstack((asmatrix(cv.GetMat(grayscale)), equ))
        grayscale = cv.fromarray(equ)

        imat = cv.GetMat(grayscale)

        ################################################################################
        # El codigo siguiente se encarga de diferencias entre blanco y negro, para esto
        # aplica calcula la diferencia entre sus vecinos en fila y despues aplica un umbral
        # de 120, sabemos que deberia ser adaptativo pero por ahora esto funcionara
        ################################################################################
        for y in range(grayscale.height):
            color = 255
            imat[y, 0] = color
            bandera = False
            for x in range(1, grayscale.width-1):
                if fabs(imat[y, x-1]-imat[y, x+1]) > 120 and not bandera:
                    imat[y, x] = color
                    if color == 255: color = 0
                    else: color = 255
                    imat[y, x+1] = color
                    bandera = True
                else:
                    imat[y, x] = color
                    bandera = False
        # Mandamos a llamar a la funcion que verifica contenga un QR code el frame recortado
        if check_qr(grayscale, thumbnail_copy):
            frames.append(grayscale)
    ##################################

    return frames

def check_qr(image, img_temp):
    """ check_qr(image, img_temp) esta funcion trabaja contando colores blancos y negros en vertical y horiontal para encontrar patrones parecidos a los de las esquinas del QR code
    """
    mat = cv.GetMat(image)
    mat_temp = cv.GetMat(img_temp)
    vertical = list()

    # Cuenta los blancos y negros en una fila
    for y in xrange(0, image.height, 3):
        actual = mat[y, 0]
        if actual == 255: temp = 1
        else: temp = -1
        color_string = list()

        for x in range(1, image.width):
            if actual == mat[y, x]:
                if actual == 255: temp += 1
                else: temp -= 1
            else:
                color_string.append(temp)
                if actual == 255:
                    temp = -1
                    actual = 0
                else:
                    temp = 1
                    actual = 255
        color_string.append(temp)
        # Este metodo verifica los patrones una vez contados los colores
        check_string_flag, x_values = check_string(color_string)
        if check_string_flag:
            for val in x_values:
                vertical.append(val)

    # Una vez encontrados patrones en horizontal esta parte hace lo mismo pero en columnas especificas en horizontal
    corner_squares = list()
    for x in vertical:
        actual = mat[0, x]
        if actual == 255: temp = 1
        else: temp = -1
        color_string = list()
        for y in range(1, image.height):
            mat_temp[y, x] = (0, 255, 0)
            if actual == mat[y, x]:
                if actual == 255:
                    temp += 1
                else:
                    temp -= 1
            else:
                color_string.append(temp)
                if actual == 255:
                    temp = -1
                    actual = 0
                else:
                    temp = 1
                    actual = 255
        color_string.append(temp)

        if check_string(color_string)[0]:
            corner_squares.append((y, x))

    if len(corner_squares) > 0:
        #print len(corner_squares)
        return True
    return False
            
def check_string(cstr):
    """ check_string(cstr) esta funcion recibe un grupo de patrones y verifica si se parece o no alguna al patron de las esquinas de un QR code"""
    pat = [-1, 1, -3, 1, -1] # Patron buscado 
    bias = [0.7, 0.7, 0.7, 0.7, 0.7] # margen de error para cada valor del patron
    pos_pat = 1
    unidad = fabs(cstr[0]) # La unidad es el valor que utiliza al empezar a buscar un nuevo patron como unidad 
    pos_range = 0
    range_values = list()

    for i in range(1, len(cstr)):
        pos_range += fabs(cstr[i])
        if pos_pat == 2:
            range_values = list()
            for p_val in range(int(pos_range-fabs(cstr[i])), int(pos_range)):
                range_values.append(p_val)

        # Esta formula calcula el error entre lo esperado y lo obtenido al comparar patrones despues aplica un umbral para decidir si es un patron correcto o no
        if fabs( (float(cstr[i])/(unidad*fabs(pat[pos_pat])))-pat[pos_pat]) < bias[pos_pat]:
            pos_pat += 1
        else:
            pos_pat = 1
            unidad = fabs(cstr[i])

        if pos_pat == len(pat):
            #print cstr, i-5
            return True, range_values
    if pos_pat == len(pat):
        return True, range_values
    else:
        return False, range_values
    

#tempora
def get_hist(image):
    imat = cv.GetMat(image)
    hist = dict()
    for i in range(256):
        hist[i] = 0
    for y in range(image.height):
        for x in range(image.width):
                hist[imat[y, x]] += 1

    return hist

def main(size=(128, 128)):
    # Se define la camara que se va a capturar y sus dimensiones
    camcapture = cv.CreateCameraCapture(-1)
    cv.SetCaptureProperty(camcapture, cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    cv.SetCaptureProperty(camcapture, cv.CV_CAP_PROP_FRAME_HEIGHT,480)

    if not camcapture:
        print "Error abriendo la camara"
        sys.exit(1)

    while False is not True:
        frame = cv.QueryFrame(camcapture)

        if frame is None:
            print "Error al leer el frame"
            break

        before = time()
        ##################################################
        # Los procesos de vision computacional se lleban a 
        # cabo en la siguiente fucion
        ##################################################
        frames = detection(frame, size = size)
        ##################################################
        #print (time()-before)
        
        for i in range(len(frames)):
            cv.ShowImage('Output'+str(i+1), frames[i])
#            cv2.moveWindow('Max', 250, 50)

        command = cv.WaitKey(10)
        if command >= 0:
            if command == 115:
                image_name = (time.ctime().replace(" ", "_"))+".png"
                cv.SaveImage( image_name, frame_copy)
                print "Imagen guardada como: ", image_name
                del image_name
            elif command == 113:
                print "Saliendo."
                cv.DestroyAllWindows()
                exit(0)

main()
