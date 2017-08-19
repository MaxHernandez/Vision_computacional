import re
import math

ref = {"KPX": 2**10, "MPX":2**20, "GPX":2**30, "TPX":2**40}

def obtener_longitud(proporcion, size):

    reg = re.search('[0-9]*', size)
    number = reg.group(0)
    
    magnitud = int(number)* ref[ (size.lstrip(number)).upper()]
    x = int(math.sqrt(magnitud/(proporcion[0]*proporcion[1])))
    print "magnitud", magnitud
    print "ancho:", (x*proporcion[0])
    print "altura:", (x*proporcion[1])
    print "Total de pixeles:", ((x*proporcion[0])*(x*proporcion[1]))
    return (x*proporcion[0]), (x*proporcion[1])

def obtener_aprox_pixeles(ancho, altura):
    if ancho*altura > ref["TPX"]:
        temp = int(ancho*altura / ref["TPX"])
        return str(temp)+" Tpx"
    elif ancho*altura > ref["GPX"]:
        temp = int(ancho*altura / ref["GPX"])
        return str(temp)+" Gpx"
    elif ancho*altura > ref["MPX"]:
        temp = int( (ancho*altura) / ref["MPX"])
        return str(temp)+" Mpx"
    elif ancho*altura > ref["TPX"]:
        temp = int(ancho*altura / ref["KPX"])
        return str(temp)+" Kpx"
    else:
        temp = ancho*altura
        return str(temp)+" pixeles"

def main():
    print "Entrada: Propocion:16:9", "5Mpx"
    ancho, altura = obtener_longitud([16, 9], "5Mpx")
    print "Entrada: ancho:", ancho, "altura:", altura 
    print obtener_aprox_pixeles(ancho, altura)

main()
