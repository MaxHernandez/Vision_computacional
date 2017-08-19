import cv, cv2
from numpy import *
from sys import exit
from time import time
from math import ceil, fabs

indice_mascara = {
    "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
    "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
    "sobel5x":[[1, 2, 0, -2, -1], [4, 8, 0, -8, -4], [6, 12, 0, -12, -6], [4, 8, 0, -8, -4], [1, 2, 0, -2, -1]],
    "sobel5y":[[-1, -4, -6, -4, -1], [-2, -8, -12, -8, -2], [0, 0, 0, 0, 0], [2, 8, 12, 8, 2], [1, 4, 6, 4, 1]],
    "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
    "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
    }

def restar(izquierda, derecha, mask = 'sobel5', umbralEsquinas = 10, umbralAngulos = 10, gx = None, gy = None):
    imatI = cv.GetMat(izquierda)
    imatD = cv.GetMat(derecha)
    gx = cv.GetMat(gx)
    gy = cv.GetMat(gy)
    max_value = 0
    votos = dict()
    for y in range(izquierda.height):
        for x in range(izquierda.width):
            value = imatI[y, x]
            value -= imatD[y, x]
            imatD[y, x] = value
            if value > max_value:
                max_value = value

    razon = 255.0 / max_value
    for y in range(izquierda.height):
        for x in range(izquierda.width):
            value = int(imatD[y, x]*razon)
#            imatD[y, x] = value
            if  value > umbralEsquinas:
#                imatD[y, x] = 255
                suma = gx[y, x] + gy[y, x]
#                if suma in votos:
#                    votos[suma] += 1
#                else:
#                    votos[suma] = 1
            else:
                imatD[y, x] = 0

#    for i in votos.keys():
#        if votos[i] > 10:
#            imatD[y, x] = 255
#        else:
#            imatD[y, x] = 0
    

def fit_colors(image, bias = 15.0):
    imat = cv.GetMat(image)
    for y in range(image.height):
        for x in range(image.width):
            R, G, B = imat[y, x]
            if fabs(R-G) > bias or fabs(R-B) > bias or fabs(B-G) > bias:
                imat[y, x] = (255, 255, 255)

def calculate_resize(actual_size, input_size): 
    max_actual = max(actual_size)
    max_input = max(input_size)
    rate_change = float(max_input) / max_actual
    return tuple([int(i*rate_change) for i in actual_size])

def detection(frame, size = (256, 256)):
#   Crear un thumbnail del frame
    image = frame
    size_frame = cv.GetSize(image)        
    thumbnail = cv.CreateImage( calculate_resize(size_frame, size), frame.depth, frame.nChannels)
    cv.Resize(frame, thumbnail)
    image = thumbnail

#   Filtrar solo colores blancos y negros
#    fit_colors(image)

#   Convertir a escala de grises
    size_thumbnail = cv.GetSize(thumbnail)
    grayscale = cv.CreateImage(size_thumbnail, 8, 1)
    cv.CvtColor(thumbnail, grayscale, cv.CV_RGB2GRAY)
    image = grayscale

#   Gaussian blur
    cv.Smooth(image, image, cv.CV_MEDIAN, 3, 3)

#    Encontrar los gradientes en horizontal y vertical
    ddepth = cv.CV_16S
    gradientx = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
    gradienty = cv.CreateMat(grayscale.height, grayscale.width, ddepth)
    cv.Sobel(grayscale, gradientx, 1, 0)
    cv.Sobel(grayscale, gradienty, 0, 1)

#   Gaussian blur
    original = cv.CloneImage(image)
    cv.Smooth(image, image, cv.CV_MEDIAN, 3, 3)
    restar(original, image, umbralEsquinas = 5.0, umbralAngulos = 10, gx = gradientx, gy = gradienty)

#    Aumentar contraste utilizando histogramas
#    equ = cv2.equalizeHist(asmatrix(cv.GetMat(image)))
#    res = hstack((asmatrix(cv.GetMat(grayscale)), equ))
#    grayscale = cv.fromarray(equ)

    ##################################
    # Mis procesos van aqui
    
    """
    imat = cv.GetMat(image)
    size = cv.GetSize(imat)
    bias = 10
    print "\n\n\nNueva imagen"
    for y in range(thumbnail.height):
        for x in range(thumbnail.width):
            R, G, B = imat[y, x]
            if fabs(R - B) > bias:
                imat[y, x] = (255, 255, 255)
            elif fabs(R - G) > bias:
                imat[y, x] = (255, 255, 255)
            elif fabs(G - B) > bias:
                imat[y, x] = (255, 255, 255)
    """

#            print grayscale[x, y],
#        print
    

    ##################################
    return [frame, image]

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
