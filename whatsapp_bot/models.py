from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    """Modelo para categorías de productos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    """Modelo para productos"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    stock = models.PositiveIntegerField(default=0)
    imagen_url = models.URLField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
    def esta_disponible(self):
        """Verifica si el producto está disponible"""
        return self.activo and self.stock > 0

class OfertaEspecial(models.Model):
    """Modelo para ofertas especiales"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    productos = models.ManyToManyField(Producto, related_name='ofertas')
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Oferta Especial'
        verbose_name_plural = 'Ofertas Especiales'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return self.titulo
    
    def esta_vigente(self):
        """Verifica si la oferta está vigente"""
        ahora = timezone.now()
        return self.activo and self.fecha_inicio <= ahora <= self.fecha_fin

class Customer(models.Model):
	name = models.CharField(max_length=200)
	phone_number = models.CharField(max_length=50, unique=True)
	email = models.EmailField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return f"{self.name} ({self.phone_number})"

class Conversation(models.Model):
	STATE_CHOICES = (
		('greeting', 'Saludo'),
		('main_menu', 'Menú Principal'),
		('browsing_products', 'Navegando Productos'),
		('product_detail', 'Detalle de Producto'),
		('adding_to_cart', 'Agregando al Carrito'),
		('checkout', 'Proceso de Pago'),
		('order_confirmation', 'Confirmación de Orden'),
		('order_status', 'Estado de Orden'),
		('customer_support', 'Atención al Cliente'),
	)
	
	HANDLER_CHOICES = (
        ('bot', 'Bot Handling'),
        ('human_requested', 'Human Support Requested'),
        ('human_active', 'Human Support Active'),
        ('resolved', 'Resolved')
    )
	
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
	current_state = models.CharField(max_length=50, choices=STATE_CHOICES, default='greeting')
	context_data = models.JSONField(default=dict, blank=True)
	active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	last_interaction = models.DateTimeField(auto_now=True)

    
	@property
	def human_support_requested(self):
		return self.handler_type == 'human_requested'
    
	def request_human_support(self):
		if self.handler_type == 'bot':
			self.handler_type = 'human_requested'
			self.save()
			# Create an entry in support queue
			from admin_dashboard.models import SupportQueue
			SupportQueue.objects.create(
				conversation=self,
				phone_number=self.phone_number
			)
			return True
		return False
    
	def assign_human_agent(self, agent):
		self.handler_type = 'human_active'
		self.last_human_agent = agent
		self.save()
    
	def return_to_bot(self):
		self.handler_type = 'bot'
		self.save()
	
	def __str__(self):
		return f"Conversación con {self.customer} - {self.current_state}"

class Message(models.Model):
	DIRECTION_CHOICES = (
		('inbound', 'Entrante'),
		('outbound', 'Saliente'),
	)
	
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
	content = models.TextField()
	media_url = models.URLField(blank=True, null=True)
	direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
	timestamp = models.DateTimeField(auto_now_add=True)
	delivered = models.BooleanField(default=False)
	read = models.BooleanField(default=False)
	whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)
	
	def __str__(self):
		return f"{self.direction} message: {self.content[:30]}"
	
	class Meta:
		ordering = ['timestamp']

class MessageTemplate(models.Model):
	name = models.CharField(max_length=100)
	content = models.TextField()
	description = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	def __str__(self):
		return self.name
	
	def render(self, context=None):
		"""Renderiza la plantilla con el contexto dado"""
		if not context:
			return self.content
			
		import re
		rendered = self.content
		# Reemplaza los placeholders {variable} con valores reales
		for key, value in context.items():
			pattern = r'\{' + key + r'\}'
			rendered = re.sub(pattern, str(value), rendered)
		return rendered
