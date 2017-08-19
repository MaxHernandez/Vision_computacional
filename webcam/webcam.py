#! /usr/bin/python
import Image, cv, cv2, time, sys

"""
Cuando se corre el programa comienza a grabar.
Teclado:
"s" -> grabara en una imagen el frame actual.
"q" -> Termina el programa
"""

def median_filter(image):
    """ El filtro solo acepta matrices como kernel"""

    mat = image
    mat_copy = cv.CloneMat(mat) 

    for i in range(mat.rows):
        for j in range(mat.cols):

            temp = [[], [], []]
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < mat.rows and l < mat.cols:
                        temp[0].append(mat_copy[i, j][0])
                        temp[1].append(mat_copy[i, j][1])
                        temp[2].append(mat_copy[i, j][2])

            pixel = list(mat_copy[i, j])
            for h in range(3):
                temp[h].sort()
                pixel[h] = temp[h][5] 
            mat_copy[i, j] = tuple(pixel)
    return mat_copy


# Convoltion or mask or filtering
def filtering(kernel, image):

    """ El filtro solo acepta matrices como kernel"""
    mat = image
    mat_copy = cv.CloneMat(mat) 

    for i in range(mat.rows):
        for j in range(mat.cols):

            sumatory = [0.0, 0.0, 0.0] # RGB
            kernel_len = len(kernel[0])
            kernel_pos = 0
            
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < mat.rows and l < mat.cols:
                        pixel = mat[h, l]
                        sumatory[0] += pixel[0]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        sumatory[1] += pixel[1]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        sumatory[2] += pixel[2]*kernel[int(kernel_pos/3)][kernel_pos%3]
                        kernel_pos += 1

            pixel = list(mat_copy[i, j])
            for h in range(3):
                pixel[h] = sumatory[h]
            mat_copy[i, j] = tuple(pixel)
    return mat_copy

def vision(image):
    mat=cv.GetMat(image)

    const = 11.0
#    kernel = [[1.0/const, 2.0/const, 1.0/const], [2.0/const, 4.0/const, 2.0/const], [1.0/const, 2.0/const, 1.0/const]] # Gaussian mask
#    kernel = [[0.0, 1.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, -1.0, 0.0]] # Diagonal prewit
    return filtering(kernel, mat)
#    return median_filter(mat)
#    return filtering(kernel, median_filter(mat))

def show_by(image, secs=10):
#    before = time.time()
#    counter = 0
    while True:
        cv.ShowImage('Max', image)
        cv2.moveWindow('Max', 250, 50)

        command = cv.WaitKey(10)
        if command >= 0:
            if command == 115:
                image_name = (time.ctime().replace(" ", "_"))+".png"
                cv.SaveImage( image_name, image)
    	        print "Imagen guardada como: ", image_name
	        del image_name
                
	    elif command == 113:
                print "Saliendo."
                cv.DestroyAllWindows()
                sys.exit(0)

            elif command == 98:
                break

#        if counter > secs:
#            break

#        now = time.time() 
#        if (now-before) > 1:
#            before = now
#            counter += 1
#            print counter, "s"

def main():
    camcapture = cv.CreateCameraCapture(0)

    cv.SetCaptureProperty(camcapture,cv.CV_CAP_PROP_FRAME_WIDTH, 640)
    cv.SetCaptureProperty(camcapture,cv.CV_CAP_PROP_FRAME_HEIGHT,480)

#    cv.SetCaptureProperty(camcapture,cv.CV_CAP_PROP_FRAME_WIDTH, 250)
#    cv.SetCaptureProperty(camcapture,cv.CV_CAP_PROP_FRAME_HEIGHT, 180)

    if not camcapture:
        print "Error opening WebCAM"
        sys.exit(1)
 
    frame_copy = None
    #if False is not True:
    while False is not True:
        frame = cv.QueryFrame(camcapture)

	if frame is None:
            print "Error al leer el frame"
            break

        if not frame_copy:
            frame_copy = cv.CreateImage((frame.width,frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)
        if frame.origin == cv.IPL_ORIGIN_TL:
            cv.Copy(frame, frame_copy)
        else:
            cv.Flip(frame, frame_copy, 0)

        cv.ShowImage('Max', frame_copy)
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
                sys.exit(0)
            elif command == 32: # 32 es un la tecla espacio
                print "Generando efecto..."
                frame_copy = vision(frame)
                print "Mostrando resultado, presione \"b\" para volver a la camara"
                show_by(frame_copy, 15)

main()
