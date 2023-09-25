import math

#Exercicio 4.1
impar = lambda n: n%2 == 1

#Exercicio 4.2
positivo = lambda n: n> 0

#Exercicio 4.3
comparar_modulo = lambda x, y: abs(x) < abs(y)

#Exercicio 4.4
cart2pol = lambda x,y : (math.hypot(x,y), math.atan2(y,x))

#Exercicio 4.5
ex5 = lambda f,g,h: lambda x, y, z: h(f(x,y), g(y,z))

#Exercicio 4.6
def quantificador_universal(lista, f):
    if  lista == []:
        return True

    if f(lista[0]):
        return quantificador_universal(lista[1:], f)

        
#Exercicio 4.8
def subconjunto(lista1, lista2):    
    if lista1 == []:
        return True

    if lista1[0] in lista2:
        return subconjunto(lista1[1:], lista2)

    return False


#Exercicio 4.9
def menor_ordem(lista, f):
    if lista == []:
        return None

    if len(lista) == 1:
        return lista[0]

    if f(lista[0], menor_ordem(lista[1:], f)):
        return lista[0]

    return menor_ordem(lista[1:], f)

#Exercicio 4.10
def menor_e_resto_ordem(lista, f):
    if lista == []:
        return None, []
    
    if len(lista) == 1:
        return lista[0], []

    menor, resto = menor_e_resto_ordem(lista[1:], f)

    if menor == None:
        return lista[0], []

    if f(lista[0], menor):
        resto += [menor]
        return lista[0], resto
    
    return menor, [lista[0]] + resto

#Exercicio 5.2
def ordenar_seleccao(lista, ordem):
    if lista == []:
        return []

    if len(lista) == 1:
        return lista

    for i in range (len(lista)):
        if  ordem(lista[i],lista[0]):
            lista[0],lista[i] = lista[i],lista[0]
    
    return [lista[0]]+ordenar_seleccao(lista[1:],ordem)
