import cv, cv2
import numpy as np
from sys import exit
from time import time
from math import ceil, fabs

"""
Cuando se corre el programa comienza a grabar.
Teclado:
"s" -> grabara en una imagen el frame actual.
"q" -> Termina el programa
"""

class QRScanner:

    def get_charstable(self, pattern):
        charstable = dict()
        length = len(pattern)

        for i in range(length-1):
            charstable[pattern[i]] = length -i -1
        return charstable

    def boyer_moore(self, string, pattern):
        charstable = self.get_charstable(pattern)

        length_pattern = len(pattern)
        length_string = len(string)

        if length_pattern > length_string:
            return
            yield
        
        i = length_pattern - 1# for the string
        j = length_pattern - 1# for the pattern
        shift = 0
        counter = 0
        bandera = True

        while i < length_string:# - length_pattern:
            if string[i] == pattern[j]:
                if shift == length_pattern-1:
                    yield i
                    bandera = False
                    counter += 1
                    i += length_pattern
                    j = length_pattern - 1
                    shift = 0
                shift += 1
                i -= 1
                j -= 1

            else:
                if string[i] in charstable:
                    i += charstable[string[i]]
                else:
                    i += length_pattern
                j = length_pattern - 1
                shift = 0
        if bandera:
            return
            yield

    def find(self, string, pattern):
        return [i for i in self.boyer_moore(string, pattern)]

    def get_mean(self, vector):
        res = 0.0
        for i in vector:
            res += i
        return int(res / len(vector))

    def binarize(self, vector, threshold = 128):
#        return self.get_mean(vector)
#        if self.get_mean(vector) > threshold:
        if vector > threshold:
            return 255
        else:
            return  0

    def find_patterns(self, image, threshold = [0.7]*5, color_pat = 'BWBWB', pat = (1, 1, 3, 1, 1), bthreshold = 128): #(color, proporcion)):
        imat = cv.GetMat(image)
        size = cv.GetSize(imat)
        bandera = False
        found_pixels_horizontal = list()

#        for x in range(size[1]):
#            for y in range(size[0]):
#                imat[x, y] = tuple( [self.binarize(imat[x, y], threshold = bthreshold)]*3 )
#                imat[x, y] = self.binarize(imat[x, y], threshold = bthreshold)
#        return 

        # Busqueda en lineas horizontales
        for x in range(size[1]):
            line = ''
            cpixel = list()
            ranges = [0]
            color_counter = 1
            color = self.binarize(imat[x, 0])

            for y in range(1, size[0]):
                pixel = self.binarize(imat[x, y])
                if pixel == color:
                    color_counter += 1
                else:
                    if color == 255: line += 'W'
                    else: line += 'B'
                    ranges.append(y)
                    cpixel.append(color_counter)
                    color = pixel
                    color_counter = 1

            if color == 255: line += 'W'
            else: line += 'B'
            ranges.append(y)
            cpixel.append(color_counter)

            for r in self.boyer_moore(line, color_pat):
                for vector in [[cpixel[j] for j in range(r, r+5)]] :
                    unidad = float(vector[-1])
                    for indice in range(1, len(vector)):

                        vector[indice] = vector[indice]/unidad

                        if fabs(pat[indice]-vector[indice]) > threshold[indice]:
                            break
                        if indice == len(vector)-1:
                            for ycord in range(ranges[r], ranges[r+5]):
                                found_pixels_horizontal.append((x, ycord))
#                                print x, ycord
                                imat[x, ycord] = (255, 0, 0)
                                #yield x, ycord
#                                bandera = True
#        return
    # Busqueda lineas verticales
        #for x in range(size[1]):
        found_pixels = list()
        for xcord, y in found_pixels_horizontal:
            line = ''
            cpixel = list()
            ranges = [0]
            color_counter = 1
            color = self.binarize(imat[0, y])

            for x in range(1, size[1]):
                pixel = self.binarize(imat[x, y])
                if pixel == color:
                    color_counter += 1
                else:
                    if color == 255: line += 'W'
                    else: line += 'B'
                    ranges.append(x)
                    cpixel.append(color_counter)
                    color = pixel
                    color_counter = 1

            if color == 255: line += 'W'
            else: line += 'B'
            ranges.append(x)
            cpixel.append(color_counter)

            for r in self.boyer_moore(line, color_pat):
                for vector in [[cpixel[j] for j in range(r, r+5)]] :
                    unidad = float(vector[-1])
                    for indice in range(1, len(vector)):

                        vector[indice] = vector[indice]/unidad
                        
                        if fabs(pat[indice]-vector[indice]) > threshold[indice]:
                            break
                        if indice == len(vector)-1:
                            for xcord in range(ranges[r], ranges[r+5]):
#                                print x, ycord
                                found_pixels.append((xcord, y))
                                imat[xcord, y] = (0, 255, 0)
#                                #yield x, ycord
#                            bandera = True

        if len(found_pixels) > 3:
            bandera = True
            
    def scan(self, image):
        self.find_patterns(image, threshold = (0.7, 0.7, 0.8, 0.8, 0.7), bthreshold = 100)

def calculate_resize(actual_size, input_size): 
    max_actual = max(actual_size)
    max_input = max(input_size)
    rate_change = float(max_input) / max_actual
    return tuple([int(i*rate_change) for i in actual_size])

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
        size_frame = cv.GetSize(frame)
        
#        thumbnail = cv.CreateImage( calculate_resize(size_frame, size), frame.depth, frame.nChannels)
#        cv.Resize(frame, thumbnail)

#        size_thumbnail = cv.GetSize(thumbnail)
#        grayscale = cv.CreateImage(size_thumbnail, 8, 1)
#        cv.CvtColor(thumbnail, grayscale, cv.CV_RGB2GRAY)

#        equ = cv2.equalizeHist(np.asmatrix(cv.GetMat(grayscale)))
#        res = np.hstack((np.asmatrix(cv.GetMat(grayscale)), equ))
#        res = cv.fromarray(equ)

        qr = QRScanner()
        qr.scan(frame)

        qr2 = QRScanner()
#        qr.scan(grayscale)

#        frame = thumbnail
#        frame = res
        ##################################################
        print (time()-before)

        cv.ShowImage('Max', frame)
        cv.ShowImage('Grayscale', grayscale)
        cv2.moveWindow('Max', 250, 50)

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
