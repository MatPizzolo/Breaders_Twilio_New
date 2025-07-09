"""
Constantes utilizadas en los manejadores de conversación del bot de WhatsApp

Este módulo contiene todos los valores constantes utilizados por los manejadores de conversación,
incluyendo nombres de estados, opciones de menú, palabras clave para detección de intenciones,
y umbrales de confianza para la clasificación de mensajes.
"""

# Identificadores de opciones de menú
MENU_VER_PRODUCTOS = '1'
MENU_HACER_PEDIDO = '2'
MENU_CONSULTAR_ESTADO = '3'
MENU_OFERTAS_ESPECIALES = '4'
MENU_ATENCION_CLIENTE = '5'

# Umbrales de confianza para detección de intenciones
INTENT_ALTA_CONFIANZA = 0.85  # Umbral de alta confianza para detección de intenciones
INTENT_MEDIA_CONFIANZA = 0.65  # Umbral de confianza media para detección de intenciones
INTENT_BAJA_CONFIANZA = 0.40  # Umbral de baja confianza para detección de intenciones

# Nombres de estados
ESTADO_SALUDO = 'saludo'
ESTADO_MENU_PRINCIPAL = 'menu_principal'
ESTADO_NAVEGANDO_PRODUCTOS = 'navegando_productos'
ESTADO_DETALLE_PRODUCTO = 'detalle_producto'
ESTADO_AGREGANDO_AL_CARRITO = 'agregando_al_carrito'
ESTADO_CHECKOUT = 'checkout'
ESTADO_ESTADO_PEDIDO = 'estado_pedido'
ESTADO_CONFIRMACION_PEDIDO = 'confirmacion_pedido'
ESTADO_OFERTAS_ESPECIALES = 'ofertas_especiales'

# Palabras clave para saludos simples
PALABRAS_SALUDO = [
    'hola', 'buenas', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos',
    'hey', 'ey', 'hi', 'hello', 'ola', 'que tal', 'qué tal', 'como va', 'cómo va'
]
ESTADO_ATENCION_CLIENTE = 'atencion_cliente'

# Grupos de palabras clave para navegación
# Menú principal y palabras clave de navegación
PALABRAS_MENU_PRINCIPAL = [
    'menu', 'menú', 'principal', 'volver al menú', 'volver al menu',
    'menú principal', 'menu principal', 'inicio', 'volver'
]

# Palabras clave de saludo con variaciones expandidas
PALABRAS_SALUDO = [
    'hola', 'buen día', 'buen dia', 'buenos días', 'buenos dias', 
    'buenas tardes', 'buenas noches', 'qué tal', 'que tal', 'cómo va', 'como va', 
    'qué onda', 'que onda', 'holis', 'saludos'
]

# Grupos de palabras clave para reconocimiento de intenciones con variaciones expandidas
PALABRAS_VER_PRODUCTOS = [
    'ver producto', 'ver productos', 'productos', 'catalogo', 'catálogo', 'milanesas', 
    'que tenés para vender', 'que tenes para vender', 'mostrame los productos',
    'quiero ver productos', 'quisiera ver productos', 'menú de productos', 'menu de productos', 
    'que vendés', 'que vendes', 'mostrame las opciones'
]

PALABRAS_HACER_PEDIDO = [
    'hacer pedido', 'hacer un pedido', 'quiero comprar', 'quisiera comprar',
    'quiero pedir', 'quisiera pedir', 'quiero ordenar', 'quisiera ordenar',
    'realizar pedido', 'realizar compra', 'me gustaría comprar', 'me gustaria comprar', 
    'me gustaría pedir', 'me gustaria pedir'
]

PALABRAS_ESTADO_PEDIDO = [
    'consultar estado', 'estado de mi pedido', 'seguimiento de pedido', 'mi pedido', 
    'donde está mi pedido', 'donde esta mi pedido', 'cuando llega mi pedido', 
    'cuándo llega mi pedido', 'tracking de mi pedido', 'rastreo de pedido',
    'revisar pedido', 'cómo va mi pedido', 'como va mi pedido', 
    'estado de mi compra', 'estado de mi orden'
]

PALABRAS_OFERTAS_ESPECIALES = [
    'ofertas', 'promociones', 'descuentos', 'ofertas especiales', 'promociones especiales',
    'promo', 'combos especiales', 'paquetes con descuento', 'liquidación', 'liquidacion',
    'ofertas del día', 'ofertas del dia', 'promociones del día', 'promociones del dia',
    'hay descuentos', 'tienen ofertas'
]

PALABRAS_ATENCION_CLIENTE = [
    'atención al cliente', 'atencion al cliente', 'servicio al cliente', 
    'hablar con alguien', 'hablar con una persona', 'hablar con un representante',
    'necesito ayuda', 'tengo un problema', 'tengo una duda', 'tengo una pregunta',
    'quiero hablar con un humano', 'quiero hablar con una persona', 
    'contactar con soporte', 'contactar con atención'
]

# Palabras clave de navegación
PALABRAS_VOLVER = [
    'volver atrás', 'volver atras', 'ir atrás', 'ir atras', 'regresar',
    'volver a categorías', 'volver a categorias', 'atrás', 'atras'
]

# Palabras clave de carrito y checkout
PALABRAS_CARRITO = [
    'carrito', 'ver carrito', 'mi carrito', 'ver mi carrito', 'finalizar compra', 
    'terminar compra', 'proceder al pago', 'ir a pagar', 'revisar carrito', 
    'revisar mi carrito', 'checkout', 'ver mis productos'
]

# Palabras clave de confirmación
PALABRAS_CONFIRMAR = [
    'confirmar', 'si', 'sí', 'aceptar', 'confirmar pedido', 'confirmar compra',
    'estoy de acuerdo', 'me parece bien', 'ok', 'okay', 'dale', 'listo'
]

PALABRAS_CANCELAR = [
    'cancelar', 'no', 'rechazar', 'cancelar pedido', 'cancelar compra',
    'no quiero', 'no me interesa', 'no gracias', 'mejor no'
]

# Mensajes predefinidos
MENSAJE_BIENVENIDA = (
    "¡Hola! En Breaders te solucionamos el almuerzo y la cena 🍽️.\n¿Estás listo/a para hacer tu pedido o tenés alguna consulta?\n\n"
    "1️⃣ Ver productos\n"
    "2️⃣ Hacer un pedido\n"
    "3️⃣ Consultar estado de pedido\n"
    "4️⃣ Ver ofertas especiales\n"
    "5️⃣ Hablar con atención al cliente"
)

MENSAJE_MENU_PRINCIPAL = (
    "Menú Principal:\n\n"
    "1️⃣ Ver productos\n"
    "2️⃣ Hacer un pedido\n"
    "3️⃣ Consultar estado de pedido\n"
    "4️⃣ Ver ofertas especiales\n"
    "5️⃣ Hablar con atención al cliente"
)

MENSAJE_VER_PRODUCTOS = (
    "Estos son nuestros productos disponibles:\n\n"
    "🥖 Milanesas de carne\n"
    "🥖 Milanesas de pollo\n"
    "🥖 Milanesas de cerdo\n"
    "🥖 Milanesas vegetarianas\n\n"
    "Responde con el nombre del producto para ver más detalles."
)

MENSAJE_HACER_PEDIDO = (
    "Para hacer un pedido, primero selecciona el producto que deseas:\n\n"
    "🥖 Milanesas de carne\n"
    "🥖 Milanesas de pollo\n"
    "🥖 Milanesas de cerdo\n"
    "🥖 Milanesas vegetarianas\n\n"
    "Responde con el nombre del producto para agregarlo a tu carrito."
)

MENSAJE_CONSULTAR_ESTADO = (
    "Para consultar el estado de tu pedido, necesito el número de pedido. "
    "Por favor, envíame el número de pedido que recibiste en tu confirmación."
)

MENSAJE_OFERTAS_ESPECIALES = (
    "¡Tenemos estas ofertas especiales para vos!\n\n"
    "🔥 2x1 en milanesas de pollo los martes\n"
    "🔥 30% de descuento en tu primera compra\n"
    "🔥 Envío gratis en pedidos mayores a $5000\n\n"
    "¿Te interesa alguna de estas ofertas?"
)

MENSAJE_ATENCION_CLIENTE = (
    "Estás en el área de atención al cliente. "
    "Por favor, describe tu consulta o problema y te ayudaremos lo antes posible."
)

MENSAJE_NO_ENTIENDO = (
    "Lo siento, no entendí tu mensaje. ¿Podrías reformularlo o elegir una opción del menú?\n\n"
    + MENSAJE_MENU_PRINCIPAL
)

MENSAJE_ERROR = (
    "Lo siento, ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente más tarde."
)

# Opciones de menú numeradas
OPCIONES_MENU_NUMERADAS = {
    'ver_productos': '1',
    'hacer_pedido': '2',
    'consultar_estado': '3',
    'ofertas_especiales': '4',
    'atencion_cliente': '5'
}

# Mapeo de intenciones a estados
MAPEO_INTENCION_ESTADO = {
    'saludo': ESTADO_SALUDO,
    'ver_productos': ESTADO_NAVEGANDO_PRODUCTOS,
    'hacer_pedido': ESTADO_AGREGANDO_AL_CARRITO,
    'consultar_estado': ESTADO_ESTADO_PEDIDO,
    'ofertas_especiales': ESTADO_OFERTAS_ESPECIALES,
    'atencion_cliente': ESTADO_ATENCION_CLIENTE
}

# Intenciones por defecto para detección
INTENCIONES_PREDETERMINADAS = [
    'saludo',
    'ver_productos',
    'hacer_pedido',
    'consultar_estado',
    'ofertas_especiales',
    'atencion_cliente',
    'cancelar_pedido',
    'pregunta_pago',
    'pregunta_producto'
]
