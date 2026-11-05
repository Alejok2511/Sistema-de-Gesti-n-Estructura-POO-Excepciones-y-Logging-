import logging
from abc import ABC, abstractmethod
from datetime import datetime

# 1. CONFIGURACIÓN DE LOGS (El archivo registrará todo sin detener el programa)
logging.basicConfig(
    filename='software_fj_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # <--- Solo debes añadir esta línea
)

# 2. EXCEPCIONES PERSONALIZADAS
class DatosInvalidosError(Exception):
    pass

class ServicioNoDisponibleError(Exception):
    pass

class ReservaError(Exception):
    pass

# 3. CLASES ABSTRACTAS
class EntidadSistema(ABC):
    @abstractmethod
    def mostrar_detalles(self):
        pass

class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre, tarifa_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = True

    # Método que será sobrescrito (Polimorfismo)
    @abstractmethod
    def calcular_costo(self, duracion, descuento=0.0):
        pass

# 4. CLASES DE DOMINIO
class Cliente(EntidadSistema):
    def __init__(self, documento, nombre):
        self.__documento = None
        self.__nombre = None
        # Usamos los setters para validar desde la creación
        self.set_documento(documento)
        self.set_nombre(nombre)

    # Encapsulamiento y validación
    def set_documento(self, documento):
        if not str(documento).isdigit() or len(str(documento)) < 5:
            raise DatosInvalidosError(f"Documento inválido: {documento}")
        self.__documento = documento

    def get_documento(self):
        return self.__documento

    def set_nombre(self, nombre):
        if not nombre or len(nombre.strip()) < 3:
            raise DatosInvalidosError(f"Nombre de cliente inválido: {nombre}")
        self.__nombre = nombre

    def get_nombre(self):
        return self.__nombre

    def mostrar_detalles(self):
        return f"Cliente: {self.__nombre} (Doc: {self.__documento})"

# Subclases de Servicios (Herencia y Polimorfismo)
class ReservaSala(Servicio):
    def calcular_costo(self, horas, descuento=0.0, impuesto=0.19):
        # Sobrecarga simulada mediante parámetros por defecto
        costo = (self.tarifa_base * horas) 
        costo_final = costo - (costo * descuento) + (costo * impuesto)
        return costo_final
        
    def mostrar_detalles(self):
        return f"Sala de Reuniones: {self.nombre} - Tarifa/hora: ${self.tarifa_base}"

class AlquilerEquipo(Servicio):
    def calcular_costo(self, dias, descuento=0.0, seguro_danos=50.0):
        costo = (self.tarifa_base * dias)
        return costo - (costo * descuento) + seguro_danos

    def mostrar_detalles(self):
        return f"Equipo: {self.nombre} - Tarifa/día: ${self.tarifa_base} (+ Seguro)"

class AsesoriaEspecializada(Servicio):
    def calcular_costo(self, sesiones, descuento=0.0):
        # Descuento extra si son más de 5 sesiones
        if sesiones > 5:
            descuento += 0.10
        return (self.tarifa_base * sesiones) * (1 - descuento)

    def mostrar_detalles(self):
        return f"Asesoría: {self.nombre} - Tarifa/sesión: ${self.tarifa_base}"

class Reserva:
    def __init__(self, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("El cliente no es válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("El servicio no es válido.")
            
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        
    def confirmar(self):
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.nombre} está ocupado.")
            
            # Bloque para procesar el pago o confirmación
            costo = self.servicio.calcular_costo(self.duracion)
            self.estado = "Confirmada"
            self.servicio.disponible = False # Ocupamos el servicio
            
        except ServicioNoDisponibleError as e:
            # Encadenamiento de excepciones
            raise ReservaError(f"No se pudo confirmar la reserva. Causa: {str(e)}") from e
        else:
            # Se ejecuta solo si el try fue exitoso
            logging.info(f"Reserva exitosa: {self.cliente.get_nombre()} reservó {self.servicio.nombre} por ${costo:.2f}")
            return True
        finally:
            # Se ejecuta siempre, haya error o no
            logging.info(f"Intento de procesamiento de reserva finalizado. Estado actual: {self.estado}")

# 5. SIMULACIÓN DEL SISTEMA (10 Operaciones)
def ejecutar_simulacion():
    print("Iniciando simulación de Software FJ... Revisa el archivo .log para ver los registros.")
    logging.info("--- INICIO DE SIMULACIÓN ---")
    
    # Datos de prueba
    servicios = [
        ReservaSala(1, "Sala A (10 personas)", 50.0),
        AlquilerEquipo(2, "Proyector 4K", 120.0),
        AsesoriaEspecializada(3, "Consultoría TI", 200.0)
    ]
    
    operaciones = [
        # 1. Cliente válido
        lambda: Cliente("10203040", "Carlos Ruiz"),
        # 2. Cliente inválido (nombre corto) - Error provocado
        lambda: Cliente("123456", "Al"),
        # 3. Cliente inválido (documento letras) - Error provocado
        lambda: Cliente("ABC", "Ana Gomez"),
        # 4. Reserva exitosa (Sala)
        lambda: procesar_reserva(Cliente("112233", "Maria Lopez"), servicios[0], 4),
        # 5. Reserva fallida (Servicio ya ocupado por Maria)
        lambda: procesar_reserva(Cliente("445566", "Juan Perez"), servicios[0], 2),
        # 6. Reserva exitosa (Equipo)
        lambda: procesar_reserva(Cliente("998877", "Luis Arce"), servicios[1], 3),
        # 7. Reserva exitosa (Asesoría)
        lambda: procesar_reserva(Cliente("554433", "Diana Solis"), servicios[2], 6),
        # 8. Error forzado de tipo (Pasando un string en vez de un Cliente)
        lambda: procesar_reserva("No soy un cliente", servicios[2], 1),
        # 9. Cálculo de costos con sobrecarga (Descuento del 20%)
        lambda: print(f"Costo con 20% descuento: ${servicios[2].calcular_costo(5, descuento=0.2):.2f}"),
        # 10. Consulta de detalles (Polimorfismo en acción)
        lambda: [print(s.mostrar_detalles()) for s in servicios]
    ]
    
    for i, operacion in enumerate(operaciones, 1):
        try:
            print(f"Ejecutando operación {i}...")
            operacion()
        except Exception as e:
            # Captura cualquier error para que el programa no se detenga
            logging.error(f"Fallo en operación {i}: {type(e).__name__} - {str(e)}")
            print(f"  -> Error capturado y guardado en log: {str(e)}")

def procesar_reserva(cliente, servicio, duracion):
    reserva = Reserva(cliente, servicio, duracion)
    reserva.confirmar()

if __name__ == "__main__":
    ejecutar_simulacion()