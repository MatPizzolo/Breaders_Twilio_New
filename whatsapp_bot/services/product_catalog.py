"""
Servicio de Catálogo de Productos

Este módulo proporciona funciones para interactuar con el catálogo de productos,
incluyendo búsqueda, filtrado y formateo de información de productos para el bot de WhatsApp.
"""
import logging
from typing import List, Dict, Any, Optional
from django.db.models import Q
from ..models import Categoria, Producto, OfertaEspecial

logger = logging.getLogger(__name__)

class ProductCatalogService:
    """
    Servicio para gestionar el catálogo de productos y proporcionar
    información formateada para el bot de WhatsApp.
    """
    
    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """
        Obtiene todas las categorías activas.
        
        Returns:
            Lista de diccionarios con información de categorías
        """
        try:
            categories = Categoria.objects.filter(activo=True)
            return [
                {
                    'id': category.id,
                    'nombre': category.nombre,
                    'descripcion': category.descripcion or ''
                }
                for category in categories
            ]
        except Exception as e:
            logger.error(f"Error al obtener categorías: {str(e)}")
            return []
    
    @staticmethod
    def get_products_by_category(category_id: int) -> List[Dict[str, Any]]:
        """
        Obtiene productos activos por categoría.
        
        Args:
            category_id: ID de la categoría
            
        Returns:
            Lista de diccionarios con información de productos
        """
        try:
            products = Producto.objects.filter(
                categoria_id=category_id,
                activo=True
            )
            return [
                {
                    'id': product.id,
                    'nombre': product.nombre,
                    'precio': float(product.precio),
                    'descripcion': product.descripcion,
                    'disponible': product.esta_disponible()
                }
                for product in products
            ]
        except Exception as e:
            logger.error(f"Error al obtener productos por categoría: {str(e)}")
            return []
    
    @staticmethod
    def search_products(query: str) -> List[Dict[str, Any]]:
        """
        Busca productos por nombre o descripción.
        
        Args:
            query: Texto de búsqueda
            
        Returns:
            Lista de diccionarios con información de productos
        """
        try:
            products = Producto.objects.filter(
                Q(nombre__icontains=query) | Q(descripcion__icontains=query),
                activo=True
            )
            return [
                {
                    'id': product.id,
                    'nombre': product.nombre,
                    'precio': float(product.precio),
                    'categoria': product.categoria.nombre,
                    'descripcion': product.descripcion,
                    'disponible': product.esta_disponible()
                }
                for product in products
            ]
        except Exception as e:
            logger.error(f"Error al buscar productos: {str(e)}")
            return []
    
    @staticmethod
    def get_product_details(product_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles de un producto específico.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Diccionario con información detallada del producto o None si no se encuentra
        """
        try:
            product = Producto.objects.get(id=product_id, activo=True)
            return {
                'id': product.id,
                'nombre': product.nombre,
                'precio': float(product.precio),
                'categoria': product.categoria.nombre,
                'descripcion': product.descripcion,
                'stock': product.stock,
                'disponible': product.esta_disponible(),
                'imagen_url': product.imagen_url or ''
            }
        except Producto.DoesNotExist:
            logger.warning(f"Producto con ID {product_id} no encontrado")
            return None
        except Exception as e:
            logger.error(f"Error al obtener detalles del producto: {str(e)}")
            return None
    
    @staticmethod
    def get_active_special_offers() -> List[Dict[str, Any]]:
        """
        Obtiene ofertas especiales activas y vigentes.
        
        Returns:
            Lista de diccionarios con información de ofertas especiales
        """
        try:
            offers = [
                offer for offer in OfertaEspecial.objects.filter(activo=True)
                if offer.esta_vigente()
            ]
            return [
                {
                    'id': offer.id,
                    'titulo': offer.titulo,
                    'descripcion': offer.descripcion,
                    'descuento': float(offer.descuento_porcentaje),
                    'codigo': offer.codigo,
                    'productos': [
                        {
                            'id': product.id,
                            'nombre': product.nombre,
                            'precio_original': float(product.precio),
                            'precio_oferta': float(product.precio * (1 - offer.descuento_porcentaje / 100))
                        }
                        for product in offer.productos.filter(activo=True)
                    ]
                }
                for offer in offers
            ]
        except Exception as e:
            logger.error(f"Error al obtener ofertas especiales: {str(e)}")
            return []
    
    @staticmethod
    def format_product_list_for_whatsapp(products: List[Dict[str, Any]]) -> str:
        """
        Formatea una lista de productos para enviar por WhatsApp.
        
        Args:
            products: Lista de diccionarios con información de productos
            
        Returns:
            Texto formateado para WhatsApp
        """
        if not products:
            return "No se encontraron productos disponibles."
        
        result = "📋 *PRODUCTOS DISPONIBLES*\n\n"
        
        for i, product in enumerate(products, 1):
            availability = "✅ Disponible" if product.get('disponible', False) else "❌ No disponible"
            result += (
                f"{i}. *{product['nombre']}*\n"
                f"   💰 ${product['precio']:.2f}\n"
                f"   {availability}\n\n"
            )
        
        result += "Para ver detalles de un producto, responde con el número o nombre del producto."
        return result
    
    @staticmethod
    def format_product_detail_for_whatsapp(product: Dict[str, Any]) -> str:
        """
        Formatea los detalles de un producto para enviar por WhatsApp.
        
        Args:
            product: Diccionario con información del producto
            
        Returns:
            Texto formateado para WhatsApp
        """
        if not product:
            return "Lo siento, no se encontró información del producto solicitado."
        
        availability = "✅ Disponible" if product.get('disponible', False) else "❌ No disponible"
        
        result = (
            f"🔍 *DETALLE DEL PRODUCTO*\n\n"
            f"*{product['nombre']}*\n\n"
            f"💰 *Precio:* ${product['precio']:.2f}\n"
            f"📦 *Categoría:* {product['categoria']}\n"
            f"🔢 *Stock:* {product['stock']}\n"
            f"📊 *Estado:* {availability}\n\n"
            f"📝 *Descripción:*\n{product['descripcion']}\n\n"
        )
        
        if product.get('imagen_url'):
            result += f"🖼️ *Imagen:* {product['imagen_url']}\n\n"
        
        result += (
            "Para agregar este producto a tu carrito, responde con:\n"
            "\"Agregar [cantidad] [nombre del producto]\"\n\n"
            "Para volver al catálogo, escribe \"volver\"."
        )
        
        return result
    
    @staticmethod
    def format_special_offers_for_whatsapp(offers: List[Dict[str, Any]]) -> str:
        """
        Formatea ofertas especiales para enviar por WhatsApp.
        
        Args:
            offers: Lista de diccionarios con información de ofertas
            
        Returns:
            Texto formateado para WhatsApp
        """
        if not offers:
            return "Actualmente no hay ofertas especiales disponibles."
        
        result = "🔥 *OFERTAS ESPECIALES* 🔥\n\n"
        
        for i, offer in enumerate(offers, 1):
            result += (
                f"{i}. *{offer['titulo']}*\n"
                f"   {offer['descripcion']}\n"
                f"   🏷️ *Descuento:* {offer['descuento']}%\n"
                f"   🎫 *Código:* {offer['codigo']}\n\n"
                f"   *Productos en oferta:*\n"
            )
            
            for j, product in enumerate(offer['productos'], 1):
                result += (
                    f"   {j}. {product['nombre']}\n"
                    f"      Precio original: ${product['precio_original']:.2f}\n"
                    f"      Precio oferta: ${product['precio_oferta']:.2f}\n\n"
                )
        
        result += "Para aprovechar una oferta, responde con el código de la oferta."
        return result
