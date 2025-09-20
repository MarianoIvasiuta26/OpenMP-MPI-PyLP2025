import threading

# Programa para simular el uso de OpenMP en Python

# Definimos las variables globales
n = 10000000
numeros = list(range(1, n + 1)) # Creamos una lista de números con 10000000 elementos
suma = 0
contador_lineas = 0

# Función para calcular la suma de los números de la lista
def calcular_suma():
    """
    Función para calcular la suma de los números de la lista
    """
    global suma
    suma_local = 0
    for num in numeros:
        suma_local += num
    suma = suma_local

# Función para contar la cantidad de líneas del texto datos.txt
def contar_lineas():
    """
    Función para contar la cantidad de líneas del texto datos.txt
    """
    global contador_lineas
    with open('datos.txt', 'r') as archivo:
        for linea in archivo:
            contador_lineas += 1

# Creamos los hilos
hilo_suma = threading.Thread(target=calcular_suma)
hilo_contar_lineas = threading.Thread(target=contar_lineas)

# Iniciamos los hilos
print("Iniciando los hilos en paralelo...")
hilo_suma.start()
hilo_contar_lineas.start()

# Esperamos a que los hilos terminen
hilo_suma.join()
hilo_contar_lineas.join()

print("Los hilos han terminado")
print("La suma de los números es:", suma)
print(f"La cantidad de líneas del texto datos.txt es: {contador_lineas}")
print("================================================")