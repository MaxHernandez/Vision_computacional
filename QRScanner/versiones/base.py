import cv, cv2
from numpy import *
from sys import exit
from time import time
from math import ceil, fabs, atan2, degrees, sqrt

indice_mascara = {
    "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
    "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
    "sobel5x":[[1, 2, 0, -2, -1], [4, 8, 0, -8, -4], [6, 12, 0, -12, -6], [4, 8, 0, -8, -4], [1, 2, 0, -2, -1]],
    "sobel5y":[[-1, -4, -6, -4, -1], [-2, -8, -12, -8, -2], [0, 0, 0, 0, 0], [2, 8, 12, 8, 2], [1, 4, 6, 4, 1]],
    "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
    "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
    }    

def restar(izquierda, derecha, mask = 'sobel5', umbralEsquinas = 10, umbralAngulos = 10, bias_color = 30.0, gx = None, gy = None, original_thumbnail = None):
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

    if max_value > 0:
        razon = 255.0 / max_value
    else:
        razon = 0.0

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

    corners = list()
    for i in votos.keys():
        if votos[i] < umbralAngulos: #original
            for cord in votos_cords[i]:
                if imatD[cord] > 10:
                    imatD[cord] = 255
                    #print imatO[cord], 
#                    R, G, B = imatO[cord]
#                    if fabs(R-G) > bias_color or fabs(R-B) > bias_color or fabs(B-G) > bias_color:
#                        imatD[cord] = 255
#                    else:
#                        imatD[cord] = 0

                    corners.append(cord)
                else:
                    imatD[cord] = 0
        else:
            for cord in votos_cords[i]:
                imatD[cord] = 0
    return corners
    

def fit_colors(image, bias = 15.0):
    imat = cv.GetMat(image)
    for y in range(image.height):
        for x in range(image.width):
            R, G, B = imat[y, x]
            if fabs(R-G) > bias or fabs(R-B) > bias or fabs(B-G) > bias:
                imat[y, x] = (255, 255, 255)

def nuevo_visitados(size):
    visitados = dict()
    for i in range(size[0]):
        for j in range(size[1]):
            visitados[i,j] = False
    return visitados

def dfs(image, size, inicio, visitados):
    siguientes = list()
    siguientes.append(inicio)

    # (y, x, y, x)
    rect = [inicio[0], inicio[1], 0, 0]
    area = 0

    while len(siguientes) > 0:
        actual = siguientes.pop(0)
#        visitados[tuple(actual)] = True
        area += 1
        image[tuple(actual)] = 0

        if actual[0] < rect[0]:
            rect[0] = actual[0]
        if actual[0] > rect[2]:
            rect[2] = actual[0]
        if actual[1] < rect[1]:
            rect[1] = actual[1]
        if actual[1] > rect[3]:
            rect[3] = actual[1]

        for l in range(int(actual[0])-1, int(actual[0])+2):
            for h in range(int(actual[1])-1, int(actual[1])+2):
                if h >= 0 and l >= 0 and l < size[0] and h < size[1]:
                    if image[l, h] == 255:# and not visitados[l, h]:
                        if not (l, h) in siguientes:
                            siguientes.append((l, h))
    return area, rect

def find_squares(image):
    rects = list()
    size = (image.height, image.width)
#    visitados = nuevo_visitados(size)
    
    imat = cv.GetMat(image)
    for y in range(size[0]):
        for x in range(size[1]):
            if imat[y, x] == 255:# and not visitados[y, x]:
                area, rect = dfs(imat, size, (y, x), visitados=None)
                area_aprox = (rect[2]-rect[0])*(rect[3]-rect[1])
                if area_aprox > 0:
                    filled_area = float(area) / area_aprox
                else:
                    filled_area = 0.0
                rects.append(rect)
                #print rect, area
    return rects 

def calculate_resize(actual_size, input_size): 
    max_actual = max(actual_size)
    max_input = max(input_size)
    rate_change = float(max_input) / max_actual
    return tuple([int(i*rate_change) for i in actual_size])

def detection(frame, size = (128, 128)):
#   Crear un thumbnail del frame
    image = frame
    frames = [frame]

    size_frame = cv.GetSize(image)
    size_thumbnail = calculate_resize(size_frame, size)
    thumbnail = cv.CreateImage(size_thumbnail , frame.depth, frame.nChannels)
    cv.Resize(frame, thumbnail)
    image = thumbnail
    original_thumbnail = cv.CloneImage(image)

#   Filtrar solo colores blancos y negros
#    fit_colors(image)

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
    cv.Smooth(image, image, cv.CV_BLUR, 18, 18)
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

    before = time()
    rects = find_squares(image)

    image = original_image
    razon = (float(size_frame[0]/size_thumbnail[0]), float(size_frame[1]/size_thumbnail[1]))
    frames.append(image)

    for i in rects:
        if i[1] == i[3] or i[0] == i[2]:
            continue
        
        pt1 = (int(i[1]*razon[0]), int(i[0]*razon[1]))
        pt2 = (int(i[3]*razon[0]), int(i[2]*razon[1]))
        rect = (pt1[0], pt1[1], pt2[0]-pt1[0], pt2[1]-pt1[1])
        cv.Rectangle(frame, pt1, pt2, (0,255,0), thickness=1, lineType=8, shift=0)

        cv.SetImageROI(frame, rect);
        tmp = cv.CreateImage(cv.GetSize(frame), frame.depth, frame.nChannels)
        cv.Copy(frame, tmp)
        cv.ResetImageROI(frame)
        
        """
        pt1 = (int(i[1]), int(i[0]))
        pt2 = (int(i[3]), int(i[2]))
        rect = (pt1[0], pt1[1], pt2[0]-pt1[0], pt2[1]-pt1[1])
        cv.SetImageROI(original_thumbnail, rect);
        tmp = cv.CreateImage(cv.GetSize(original_thumbnail), original_thumbnail.depth, original_thumbnail.nChannels)
        cv.Copy(original_thumbnail, tmp)
        cv.ResetImageROI(original_thumbnail)
        size_thumbnail = cv.GetSize(original_thumbnail)
        thumbnail = tmp
        """
        
        size_thumbnail = calculate_resize(cv.GetSize(tmp), size)
        thumbnail = cv.CreateImage(size_thumbnail , tmp.depth, tmp.nChannels)
        cv.Resize(tmp, thumbnail)
        
        thumbnail_copy = cv.CloneImage(thumbnail)
        #fit_colors(thumbnail, bias = 15.0)
        """
        thumbnail = tmp
        size_thumbnail  = cv.GetSize(tmp)
        """
        grayscale = cv.CreateImage(size_thumbnail, 8, 1)
        cv.CvtColor(thumbnail, grayscale, cv.CV_RGB2GRAY)

        equ = cv2.equalizeHist(asmatrix(cv.GetMat(grayscale)))
        res = hstack((asmatrix(cv.GetMat(grayscale)), equ))
        grayscale = cv.fromarray(equ)

        """
        hist =  get_hist(grayscale)
        fl = open('hist.dat', 'w')
        keys = hist.keys()
        for i in keys:
            fl.write(str(i)+' '+str(hist[i])+'\n')
        fl.close()
        threshold = 255
        for i in range(100, 200):
            if hist[i] < threshold:
                threshold = i

        threshold = 128
        cv.Threshold(grayscale, grayscale, threshold, 255, cv2.THRESH_BINARY)
        """

        """
        ddepth = cv.CV_16S
        gx = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
        gy = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
        cv.Sobel(grayscale, gx, 1, 0)
        cv.Sobel(grayscale, gy, 0, 1)
        imat = cv.GetMat(grayscale)
        for y in range(grayscale.height):
            for x in range(grayscale.width):
                cord = (y, x)
                imat[cord] = sqrt(gx[cord]**2 + gy[cord]**2)
        """

        imat = cv.GetMat(grayscale)

        # this part of the code chech horizontal neighbors to know if there is a border in there
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
        if check_qr(grayscale, thumbnail_copy):
            frames.append(grayscale)
#            frames.append(thumbnail_copy)
    ##################################
    return frames

def check_qr(image, img_temp):
    mat = cv.GetMat(image)
    mat_temp = cv.GetMat(img_temp)
    vertical = list()

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
        check_string_flag, x_values = check_string(color_string)
        if check_string_flag:
            for val in x_values:
                vertical.append(val)

    corner_squares = list()
#    for x in range(len(vertical)):
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
    pat = [-1, 1, -3, 1, -1]
    bias = [0.5, 0.5, 1.0, 0.5, 0.5]
    pos_pat = 1
    unidad = fabs(cstr[0])
    pos_range = 0
    range_values = list()

#    print cstr
    for i in range(1, len(cstr)):
        pos_range += fabs(cstr[i])
        if pos_pat == 2:
            range_values = list()
            for p_val in range(int(pos_range-fabs(cstr[i])), int(pos_range)):
                range_values.append(p_val)

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
        # Los procesos de vision computacional se procesan
        # en la siguiente fucion
        ##################################################
        frames = detection(frame, size = size)
        ##################################################
        print (time()-before)
        
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
