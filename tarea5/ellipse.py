#!/usr/bin/python
from PIL import Image, ImageDraw, ImageFont
import sys, time, random, math


def gradient(image, mask_type='prewitt'):
    indice_mascara = {
        "sobelx":[[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
        "sobely":[[1.0, 2.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -2.0, -1.0]],
        "prewittx":[[-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0], [-1.0, 0.0, 1.0]],
        "prewitty":[[1.0, 1.0, 1.0], [0.0, 0.0, 0.0], [-1.0, -1.0, -1.0]]
        }

    pic_copy = (image.copy()).load()
    pic = image.load()
    gradient_values = dict()
    kernelx = indice_mascara[mask_type+'x']
    kernely = indice_mascara[mask_type+'y']
    max_value = 0
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            gx, gy = (0.0, 0.0)
            kernel_len = len(kernelx[0])
            kernel_pos = 0
            for h in range(i-1, i+2):
                for l in range(j-1, j+2):
                    if h >= 0 and l >= 0 and h < image.size[0] and l < image.size[1]:
                        pixel = pic_copy[h, l]
                        suma = 0
                        for s in pixel:
                            suma += s
                        pixel  = suma / len(pixel)

                        gx += pixel*kernelx[int(kernel_pos/3)][kernel_pos%3]
                        gy += pixel*kernely[int(kernel_pos/3)][kernel_pos%3]
                        kernel_pos += 1

            gradiente = int(math.sqrt(math.pow(gx, 2) + math.pow(gy, 2)))
            pic[i, j] = tuple([gradiente]*3)
            if gx != 0.0:
                gradient_values[i, j] = gy / gx
            else:
                gradient_values[i, j] = 1000

            if pic[i, j][0] > max_value:
                max_value = pic[i, j][0]
    return max_value, gradient_values

def normalizar(image, max_value):
    pic = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            (R, G, B) = pic[i,j]
            if max_value > 0:
                R = G = B = int( (float(R)/max_value)*255 )
            else:
                R = G = B = 0
            pic[i,j] = (R, G, B)

def filtro_umbral(image, umbral=128):
    puntos_borde = list()
    pic = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):

            if type(pic[i, j]) == type(0):
                if pic[i, j] < umbral:
                    pic[i, j] = 0
                else:
                    pic[i, j] = 255
                continue

            if i < 5 or i > image.size[0]-5 or j < 5 or j > image.size[1]-5:
                pic[i,j] = (0,0,0)
                continue            
 
            colors = list(pic[i,j])
            if colors[0] < umbral:
                colors[0] = 0
            else:
                puntos_borde.append((i, j))
                colors[0] = 255
            colors[1] = colors[2] = colors[0]

            pic[i,j] = tuple(colors)
    return pic, puntos_borde

def cluster_edges(border_points):
    groups = list()

    while len(border_points) > 0:
        visitados = dict()
        actual = list()
        next = [border_points[0]]
    
        while len(next) > 0:
            cord = next.pop(0)
            visitados[cord] = True
            actual.append(cord)
            border_points.pop(border_points.index(cord))

            for x in range(cord[0]-1, cord[0]+2):
                for y in range(cord[1]-1, cord[1]+2):
                    if (x, y) in border_points and not (x,y) in next:
                        next.append((x,y))
        groups.append(actual)
    return groups

def border_detection(picture, output="output.png", umbral=125):
    max_values, gradient_values = gradient(picture)
    pseudo_promedio = normalizar(picture, max_values)
    pic, puntos_borde = filtro_umbral(picture, umbral=umbral)
    puntos_borde = cluster_edges(puntos_borde)
    return puntos_borde, gradient_values

def find_circle(image):
    pic = image.load()
    circles = list()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if pic[x, y] == (255, 255, 255):
                circles.append([x,y])
    return circles

class DrawLine:

    def __init__(self, image, pressure = 5):
        self.image = image
        self.pic = image.load()
        self.pressure = pressure

    def draw(self, line, inicio = 0, direccion = 1):
        x = inicio
        while x >= 0 and x < self.image.size[0]:
#        for x in range(inicio, self.image.size[0]*direccion):
            y = int((line[0]*x) + line[1])
            if y >= 0 and y < self.image.size[1]: 
                self.pic[x, y] += self.pressure
            else:
                break
            x += direccion

def calculate_center_line(pixel1, pixel2, gradient1, gradient2, image, draw_line):
#    draw = ImageDraw.Draw(image)
    
    r = 2
#    draw.ellipse((pixel1[0]-r, pixel1[1]-r, pixel1[0]+r, pixel1[1]+r), fill=(0, 255, 0))
#    draw.ellipse((pixel2[0]-r, pixel2[1]-r, pixel2[0]+r, pixel2[1]+r), fill=(0, 0, 255))

    tangent1 = [gradient1, pixel1[1]-(gradient1*pixel1[0])] # [m, b] mx+b = y
    tangent2 = [gradient2, pixel2[1]-(gradient2*pixel2[0])]

#    line = (0, (tangent1[0]*0 + tangent1[1]) ,128, (tangent1[0]*128 + tangent1[1]))
#    draw.line(line, fill=(0, 255, 0))
#    line = (0, (tangent2[0]*0 + tangent2[1]) ,128, (tangent2[0]*128 + tangent2[1]))
#    draw.line(line, fill=(0, 0, 255))

    
    # calcular interseccion entre tangentes
    x = float(tangent2[1]-tangent1[1]) / (tangent1[0]-tangent2[0])
    y = tangent1[0]*x+ tangent1[1]
    interseccion = (x, y)

    # calcular punto medio entre puntos
    medio = ( (pixel1[0]+pixel2[0])/2, (pixel1[1]+pixel2[1])/2 )

    # calcular linea entre punto medio y el punto de la interseccion de las tangentes
    if (interseccion[0]-medio[0]) != 0:
        m = (interseccion[1]-medio[1] ) / (interseccion[0]-medio[0])
    else:
        m = 1000
    
    b = medio[1] - (m*medio[0])
    center_line = [m, b]

    if (interseccion[0]-medio[0]) < 0.0:
        direccion = 1
    else:
        direccion = -1

    draw_line.draw(center_line, inicio = medio[0], direccion = direccion)

#    line = (0, (center_line[0]*0 + center_line[1]) ,128, (center_line[0]*128 + center_line[1]))
#    draw.line(line, fill=255)

def find_centers(image, border_points, gradient_values, output):
    imageEllipse = Image.new('L', image.size, (0))
#    ellipseDraw = ImageDraw.Draw(imageEllipse)
    draw_line = DrawLine(imageEllipse, pressure = 5)

    for i in range(len(border_points)):
        border_pixels = len(border_points[i])-1
        for j in range(len(border_points[i]) ):
            pixel1 = random.randint(0, border_pixels/2)
            pixel1 = border_points[i][pixel1]
            pixel2 = random.randint(border_pixels/2, border_pixels)
            pixel2 = border_points[i][pixel2]

            if gradient_values[pixel1] != gradient_values[pixel2]:
                calculate_center_line(pixel1, pixel2, gradient_values[pixel1], gradient_values[pixel2], image, draw_line)

    return imageEllipse

def detect_center(image):
    ellipses = list()
    pic = image.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            if pic[x,y] == 255:
                ellipses.append((x,y))
    
    ellipses = cluster_edges(ellipses)
    centers = list()
    print len(ellipses)
    for i in ellipses:
        x, y = (0, 0)
        for j in i:
            x += j[0]
            y += j[1]
        x = int(float(x)/len(i))
        y = int(float(y)/len(i))
        centers.append((x, y))
    return centers

def random_orange():
    return (255, random.randint(0,150), random.randint(0, 50))

def ellipse_detection(image_name, output="output.png", size=(128, 128)):
    image = Image.open(image_name)
    original_image = image.copy()

    image.thumbnail(size, Image.ANTIALIAS)

    border_points, gradient_values = border_detection(image, output="output.png", umbral=60)
    imageEllipse = find_centers(image, border_points, gradient_values, output)
    imageEllipse.save('grayscale_'+output)
    filtro_umbral(imageEllipse, umbral = 130)
    centers = detect_center(imageEllipse)

    pic = image.load()
    dimensiones = list()
    for c in centers:
        
        actual = list(c[:])
        horizontal = 0
        while pic[tuple(actual)] != (255, 255, 255):
            actual[0] += 1
            horizontal += 1
            if horizontal > size[0]:
                break

        actual = list(c[:])
        vertical = 0
        while  pic[tuple(actual)] != (255, 255, 255):
            actual[1] += 1
            vertical += 1
            if vertical > size[1]:
                break


        dimensiones.append((horizontal, vertical))

    razon = list(image.size)
    image = original_image
    razon[0] = float(image.size[0]) / razon[0]
    razon[1] = float(image.size[1]) / razon[1]
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", 18)
    r = 5
    print 'Porcentaje de diagonales de las ellipses respecto al digonal de la imagen:'
    for i in range(len(centers)):
        nombre = 'E'+str(i+1)
        print nombre+':'
        print '    Diagonal horizontal:', (float(dimensiones[i][0])*100/image.size[0])
        print '    Diagonal vertical:', (float(dimensiones[i][0])*100/image.size[0])
        x = int(centers[i][0]*razon[0])
        y = int(centers[i][1]*razon[1])
        draw.text((x, y+(r*2)), nombre, fill=(0, 255, 0), font=font)
        draw.ellipse((x-dimensiones[i][0]*razon[0], y-dimensiones[i][1]*razon[1], x+dimensiones[i][0]*razon[0], y+dimensiones[i][1]*razon[1]), outline = random_orange())
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(0, 0, 255))
    image.save(output)


def main():
    before = time.time()
    ellipse_detection(sys.argv[1])
    print "Tiempo de corrida:", (time.time() - before)

main()
