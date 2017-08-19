#!/usr/bin/python                                                                                                                                                     
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math

class PixelH:
    def __init__(self, image_matrix, image, group_bias, salto, cambio):
        self.image_matrix = image_matrix
        self.cota_superior = min(image.size)-1
        self.cota_inferior = 1
        self.group_bias = group_bias
        self.salto = salto
        self.cambio = cambio

    def instancia_inicial(self):
        inicial = dict()
        for c in self.image_matrix.keys():
            inicial[c] = random.randint(self.cota_inferior, self.cota_superior)
        return inicial

    def modificar_solucion(self, solucion):
        c = random.choice(solucion.keys())
        if random.choice([True, False]):
            if solucion[c] + self.cambio < self.cota_superior:
                solucion[c] += self.cambio
        else:
            if solucion[c] - self.cambio > self.cota_inferior:
                solucion[c] -= self.cambio

    def regresar_solucion(self, solucion):
        resultado = dict()
        frequency = dict()
        for c in solucion.keys():
            r = solucion[c]
            centro = (int( c[0] - r * self.image_matrix[c][0]), int( c[1] - r * self.image_matrix[c][1]))
            centro = ((centro[0]/self.salto)*self.salto, (centro[1]/self.salto)*self.salto)

            resultado[c] = centro
            if not centro in frequency:
                frequency[centro] = 1
            else:
                frequency[centro] += 1

        prom = 0
        values = frequency.values()
        for i in values:
            prom += i
        bias = prom/len(values)

        return resultado, frequency

    def funcion_objetivo(self, solucion):
        frequency = dict()
        for c in solucion:
            r = solucion[c] 
            centro = (int( c[0] - r * self.image_matrix[c][0]), int( c[1] - r * self.image_matrix[c][1]))
            centro = ((centro[0]/self.salto)*self.salto, (centro[1]/self.salto)*self.salto)

            if not centro in frequency:
                frequency[centro] = 1
            else:
                frequency[centro] += 1

        values = list()
        for i in frequency.values():
            if not i in values:
                values.append(i)
        values.sort()
        resultado = 0
        for i in range(1, len(values)):
            resultado += values[i] - values[i-1]
        return resultado

    def busqueda_voraz(self, maxReinicios, maxIntentos):
        modificado = None
        actual = None
        mejor = self.instancia_inicial()
         
        for reinicios in range(maxReinicios):
            actual = self.instancia_inicial()         
            paso = 0
 
            print "Intento de busqueda de mejor solucion:", (reinicios+1)
            for intentos in range(maxIntentos):
                modificado = dict(actual)
                self.modificar_solucion(modificado)
 
                objetivo_modificado = self.funcion_objetivo(modificado)
                objetivo_actual = self.funcion_objetivo(actual)
 
                if objetivo_modificado <= objetivo_actual:
                    paso += 1
                    actual = modificado
                intentos += 1
 
            obj_actual = self.funcion_objetivo(actual)
            obj_mejor = self.funcion_objetivo(mejor)

            if obj_actual >= obj_mejor:
                mejor = actual
 
        return self.regresar_solucion(mejor)

def get_circle_pixels(image, mask_type="sobel", border_bias = 100.0, group_bias = 15, salto = 12, maxReinicios=5, maxIntentos=200, cambio = 25):
    indice_mascara = {
        "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
        "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
        "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
        "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
        }

    pic = image.load()
    pic_copy = (image.copy()).load()
    kernelx = indice_mascara[mask_type+'x']
    kernely = indice_mascara[mask_type+'y']

    #Line detection variables 
    image_matrix = dict()
    frequency = dict()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            gx, gy = (0.0, 0.0)
            kernel_len = len(kernelx[0])
            kernel_pos = 0
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        pixel = pic_copy[h, l]
                        pixel = max(pixel)/len(pixel)
                        gx += pixel*kernelx[int(kernel_pos/3)][kernel_pos%3]
                        gy += pixel*kernely[int(kernel_pos/3)][kernel_pos%3]
                        kernel_pos += 1

            gradiente = math.sqrt(math.pow(gx, 2) + math.pow(gy, 2))
            if math.fabs(gradiente) > border_bias:
               # circle detection
                theta = math.atan2(gy, gx)
                image_matrix[i,j] = (math.cos(theta+math.radians(90.0)), math.sin(theta+math.radians(90.0)), 0)

    print "Terminado calculo de angulos, corriendo heuristico"
    heuristic = PixelH(image_matrix, image, group_bias, salto, cambio)
    image_matrix, frequency = heuristic.busqueda_voraz(maxReinicios, maxIntentos)

    return image_matrix, frequency


def random_yellow():
    return (255, random.randint(100,255), random.randint(0, 50))

def draw_lines(image, frequency, circle_matrix):
    pic = image.load()
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 18)
    draw = ImageDraw.Draw(image)
    counter = 1
    colors = dict()
    for i in frequency.keys():
#        colors[i] = random_yellow()
        r = 2
        draw.ellipse((i[0]-r, i[1]-r, i[0]+r, i[1]+r), fill=(0, 255, 0))
        draw.text((i[0]+r+3, i[1]), ('C'+str(counter)), fill=(0, 255, 0), font=font)
        print 'C'+str(counter)
        counter += 1

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            try:
                if circle_matrix[i, j] in frequency:
                    pic[i,j] = (255, 0, 0)#colors[circle_matrix[i, j]]
                    pic[i,j] = colors[ircle_matrix[i, j]]
            except:
                pass
    return image

def circle_detection(image_name, output="output.png"):
    image = Image.open(image_name)
    circle_matrix, frequency = get_circle_pixels(image)
    draw_lines(image, frequency, circle_matrix)

    image.save(output)

def main():
    before = time.time()
    circle_detection(sys.argv[1])
    print "Tiempo de corrida:", (time.time() - before)

main()
