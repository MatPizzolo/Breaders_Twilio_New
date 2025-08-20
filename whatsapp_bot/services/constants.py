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

# Palabras clave de saludo con variaciones expandidas
PALABRAS_SALUDO = [
    'hola', 'buen día', 'buen dia', 'buenos días', 'buenos dias', 
    'buenas tardes', 'buenas noches', 'qué tal', 'que tal', 'cómo va', 'como va', 
    'qué onda', 'que onda', 'holis', 'saludos'
]

# Grupos de palabras clave para navegación
# Menú principal y palabras clave de navegación
PALABRAS_MENU_PRINCIPAL = [
    'menu', 'menú', 'principal', 'volver al menú', 'volver al menu',
    'menú principal', 'menu principal', 'inicio', 'volver'
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
    "Hola, soy Fernanda, responsable del área de atención online.\n"
    "Estoy a disposición para asesorarte en lo que necesites. ¿Cómo puedo ayudarte?\n\n"
    "📲 Elegí una opción y escribí el número para avanzar\n"
    "1️⃣ Ver Productos / Descuentos / Promociones\n"
    "2️⃣ Delivery – ¿Llegan a mi zona? Zona / día / Compra mínima\n"
    "3️⃣ ¿Cómo lo recibo? ¿Cómo lo manipulo congelado? ¿Cómo lo cocino?\n"
    "4️⃣ Recetas fáciles\n"
    "5️⃣ Post-venta / Sugerencias / Atención directa"
)

MENSAJE_MENU_PRINCIPAL = (
    "📲 Elegí una opción y escribí el número para avanzar\n\n"
    "1️⃣ Ver Productos / Descuentos / Promociones\n\n"
    "2️⃣ Delivery – ¿Llegan a mi zona? Zona / día / Compra mínima\n\n"
    "3️⃣ ¿Cómo lo recibo? ¿Cómo lo manipulo congelado? ¿Cómo lo cocino?\n\n"
    "4️⃣ Recetas fáciles\n\n"
    "5️⃣ Post-venta / Sugerencias / Atención directa"
)

MENSAJE_VER_PRODUCTOS = (
    "🛒 Te muestro a continuación todo sobre nuestros productos, precios y beneficios:\n\n"
    "1️⃣ Ver LISTA DE PRODUCTOS POR CATEGORIAS\n"
    "📲 Escribí el número 1 para ver nuestros productos por categorías\n\n"
    "2️⃣ Ver precios PROMOCIONES GENERALES\n"
    "👉click aca:\n"
    "https://breaders.com.ar/categoria-producto/promos/\n\n"
    "3️⃣ Ver precios COMBOS SIN GLUTEN\n"
    "👉click aca:\n"
    "https://breaders.com.ar/categoria-producto/promociones-sin-gluten/\n\n"
    "4️⃣ Ver precios CONGELADOS y GUARNICIONES\n"
    "👉click aca:\n"
    "https://breaders.com.ar/categoria-producto/acompanamientos/\n\n"
    "5️⃣ FORMAS DE PAGO\n\n"
    "• Efectivo / Cash (10% DESCUENTO)\n"
    "• Débito\n"
    "• Crédito\n"
    "• Transferencia\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_PRODUCTOS_POR_CATEGORIAS = (
    "📲 Elegí una opción y escribí el número para avanzar\n\n"
    "1️⃣ MILANESAS\n"
    "2️⃣ CONGELADOS"
)

MENSAJE_MILANESAS = (
    "- LÍNEA TRADICIONAL\n"
    "Rebozado: Blend de distintos panes artesanales, horneados y luego molidos. Textura clásica.\n\n"
    "• POLLO\n"
    "• CARRÉ DE CERDO DESHUESADO\n"
    "• NALGA\n"
    "• PECETO\n"
    "• BIFE DE CHORIZO\n"
    "• ENTRAÑA\n"
    "• LOMO\n"
    "• VACÍO\n"
    "• MERLUZA\n\n"
    "- LÍNEA CRISPY\n"
    "Rebozado: Blend de panko blanco y panko naranja, 100% panko. Crujiente por fuera, textura suave por dentro.\n\n"
    "• POLLO\n"
    "• BIFE DE CHORIZO\n"
    "• ENTRAÑA\n"
    "• MERLUZA\n\n"
    "- LÍNEA SIN GLUTEN\n"
    "Elaboradas en espacio libre de contaminación cruzada, con productos certificados SIN TACC y packaging termo sellado de seguridad para garantizar su trazabilidad.\n\n"
    "• POLLO\n"
    "• POLLO BREADERS\n"
    "• CARRÉ DE CERDO DESHUESADO\n"
    "• NALGA\n"
    "• PECETO\n"
    "• BIFE DE CHORIZO\n\n"
    "- LÍNEA KETO (LOW CARB – SIN GLUTEN)\n"
    "Rebozado Premium: Harina de castañas de cajú, harina de almendras, harina de coco, maní granulado y ajo confitado.\n\n"
    "• POLLO\n"
    "• PECETO\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_CONGELADOS = (
    "📲 Elegí una opción y escribí el número para avanzar\n\n"
    "1️⃣ ACOMPAÑAMIENTOS Y GUARNICIONES\n"
    "2️⃣ TARTAS INDIVIDUALES\n"
    "3️⃣ PIZZAS MASA MADRE (8 PORCIONES)"
)

MENSAJE_ACOMPAÑAMIENTOS = (
    "- ACOMPAÑAMIENTOS\n\n"
    "• NUGGETS DE POLLO CRISPY\n"
    "• MEDALLON DE POLLO CRISPY\n"
    "• MEDALLON DE POLLO CRISPY RELLENO (MUZZARELLA)\n"
    "• HAMBURGUESA (BLEND LOMO-BIFE DE CHORIZO)\n"
    "• HAMBURGUESA DE POLLO\n\n"
    "- GUARNICIONES\n\n"
    "• BOCADITOS DE ESPINACA REBOZADOS\n"
    "• BOCADITO DE ESPINACA REBOZADOS RELLENOS (MUZZARELLA)\n"
    "• BOCADITO DE CALABAZA Y MUZZARELLA\n"
    "• BASTONES DE POLLO FINAS HIERBAS\n"
    "• DINOSAURIOS DE POLLO\n"
    "• BASTONES DE MUZZARELLA REBOZADOS\n"
    "• PAPAS BASTÓN, NOISETTE, SMILES\n"
    "• CROQUETAS DE PAPA RELLENAS JAMON Y MUZZARELLA\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_PROMOCIONES_GENERALES = (
    "🛒 PROMOCIONES GENERALES\n\n"
    "Aquí puedes ver todas nuestras promociones generales.\n"
    "Para más detalles, visita: https://breaders.com.ar/categoria-producto/promos/\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_COMBOS_SIN_GLUTEN = (
    "🍞 COMBOS SIN GLUTEN\n\n"
    "Descubre nuestros deliciosos combos sin gluten, elaborados en espacios libres de contaminación cruzada.\n"
    "Para más detalles, visita: https://breaders.com.ar/categoria-producto/promociones-sin-gluten/\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_CONGELADOS_GUARNICIONES = (
    "🍗 CONGELADOS Y GUARNICIONES\n\n"
    "Explora nuestra variedad de productos congelados y guarniciones para complementar tus comidas.\n"
    "Para más detalles, visita: https://breaders.com.ar/categoria-producto/acompanamientos/\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_FORMAS_PAGO = (
    "💰 FORMAS DE PAGO\n\n"
    "• Efectivo / Cash (10% DESCUENTO)\n"
    "• Débito\n"
    "• Crédito\n"
    "• Transferencia\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_TARTAS = (
    "- MASA TRADICIONAL\n\n"
    "• JAMON Y QUESO\n"
    "• POLLO Y PUERRO\n"
    "• CEBOLLA Y QUESO\n"
    "• CALABAZA\n"
    "• ZAPALLITOS\n"
    "• CAPRESE\n\n"
    "- MASA INTEGRAL\n\n"
    "• CALABAZA Y VERDURA\n"
    "• ZANAHORIA Y VERDEO\n"
    "• PUERRO Y CHAMPIGNON\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_PIZZAS = (
    "- PIZZAS MASA MADRE (8 PORCIONES)\n\n"
    "• MUZZARELLA\n"
    "• FUGAZZETTA\n"
    "• JAMON Y MORRONES\n"
    "• JAMON Y PROVOLONE\n"
    "• PROVOLONE Y VERDEO\n"
    "• CHAMPIGNONES\n"
    "• NAPOLITANA AL PESTO\n"
    "• CUATRO QUESOS\n"
    "• QUESO AZUL c/ PERAS\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_HACER_PEDIDO = (
    "📦 Te contamos cómo funciona nuestro sistema de envíos para que sepas si llegamos a tu casa, qué día pasamos y qué necesitas para recibir tu pedido.\n\n"
    "📲 Elegí una opción y escribí el número para avanzar\n\n"
    "1️⃣ ¿Entregan en mi zona? ¿Qué día y en qué horario?\n"
    "2️⃣ ¿Cuál es el monto mínimo de compra?\n"
    "3️⃣ ¿Qué pasa si cuando llega no estoy en casa?"
)

MENSAJE_CONSULTA_ZONA = (
    "Por favor, escribí el nombre de tu barrio o zona para verificar si hacemos envíos allí."
)

MENSAJE_MONTO_MINIMO = (
    "💰 El monto mínimo para realizar un pedido con envío a domicilio es $44.990.\n\n"
    "🚚 El envió es gratis en todas las zonas a las que llegamos. (CABA Y GBA)\n\n"
    "📦 Si elegís la opción de abonar tu pedido en efectivo / cash al recibirlo en casa contás con un 10% de descuento sobre el total de tu compra.\n\n"
    "🛒 Podés hacer tu pedido ahora mismo desde la web, y coordinar el envío de forma simple y segura.\n"
    "👉 Click acá:\n"
    "https://breaders.com.ar/\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_NO_ESTOY = (
    "📬 No te preocupes. Tenés varias opciones para recibir tu pedido sin problemas:\n"
    "1. ⏱️ Si estás demorado unos minutos, podemos esperarte hasta 10 minutos sin problema.\n"
    "2. 🧍‍♂️ Podés dejarlo encargado a alguien de confianza (portero, vecino, familiar).\n"
    "3. 📦 Podemos dejarlo en un punto seguro, si nos lo indicás con anticipación (como una portería o comercio amigo).\n"
    "4. 🔁 Podés reprogramar la entrega para el próximo día disponible en tu zona.\n\n"
    "🛒 ¿Querés que lo dejemos programado ya mismo?\n"
    "👉 Click acá: https://breaders.com.ar/\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_MANIPULACION = (
    "¿Cómo manipular y cocinar nuestros productos?\n\n"
    "Próximamente tendremos información detallada sobre la manipulación y cocción de nuestros productos.\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_RECETAS = (
    "Recetas fáciles con nuestros productos\n\n"
    "Próximamente compartiremos deliciosas recetas que podrás preparar con nuestros productos.\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_ATENCION_CLIENTE = (
    "Post-venta / Sugerencias / Atención directa\n\n"
    "Para consultas específicas, sugerencias o atención personalizada, por favor contáctanos a través de:\n\n"
    "📧 Email: atencion@breaders.com.ar\n"
    "📞 Teléfono: 11-XXXX-XXXX\n\n"
    "Un representante de nuestro equipo te responderá a la brevedad.\n\n"
    "📲 Escribí \"Volver\" para regresar al menú anterior."
)

MENSAJE_CONSULTAR_ESTADO = (
    "Para consultar el estado de tu pedido, necesitamos tu número de orden. ¿Podrías proporcionarnos el número de orden que recibiste al realizar tu compra?"
)

MENSAJE_OFERTAS_ESPECIALES = (
    "¡Tenemos promociones especiales esta semana! Aprovechá nuestros combos con descuentos en milanesas y productos congelados. Visitá nuestra página web para ver todas las ofertas disponibles: https://breaders.com.ar/promociones"
)

MENSAJE_NO_ENTIENDO = "Lo siento, no entendí tu mensaje. ¿Podrías reformularlo o indicarme en qué puedo ayudarte?"

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
