#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test avanzado para el bot de WhatsApp de Breaders.
Este script envía mensajes más complejos y específicos para probar
la capacidad de detección de intenciones del bot.
"""

import os
import sys
import json
import requests
import time
from typing import Dict, Any, Optional

# Configuración del servidor
BASE_URL = "http://localhost:8000"
WEBHOOK_URL = "/webhook/whatsapp/"

def print_response(response):
    """
    Imprime la respuesta HTTP de manera formateada.
    
    Args:
        response: Objeto de respuesta de requests
    """
    print("\n==================================================\n")
    print(f"Status Code: {response.status_code}\n")
    
    print("Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print("\nContent:")
    print(response.text)
    
    print("\n==================================================\n")

def simulate_whatsapp_message(message: str, from_number: str = "whatsapp:+5491112345678") -> requests.Response:
    """
    Simula un mensaje de WhatsApp enviando una solicitud POST al webhook.
    
    Args:
        message: El contenido del mensaje
        from_number: El número de teléfono del remitente (formato Twilio)
        
    Returns:
        Objeto de respuesta de requests
    """
    # Datos que Twilio enviaría en una solicitud real
    payload = {
        "Body": message,
        "From": from_number,
        "To": "whatsapp:+14155238886",  # Número de Twilio
        "SmsMessageSid": f"SM{int(time.time())}",
        "NumMedia": "0",
        "ProfileName": "Usuario de Prueba",
        "WaId": from_number.replace("whatsapp:", ""),
        "SmsStatus": "received"
    }
    
    # Enviar solicitud POST al webhook
    url = f"{BASE_URL}{WEBHOOK_URL}"
    response = requests.post(url, data=payload)
    return response

def run_advanced_test():
    """
    Ejecuta un flujo de prueba avanzado con mensajes más complejos y específicos.
    """
    print("\n🔍 INICIANDO PRUEBA AVANZADA DEL BOT DE WHATSAPP 🔍\n")
    
    # Lista de mensajes de prueba avanzados
    advanced_messages = [
        # Saludos complejos
        "Buenas tardes, ¿cómo están?",
        "Hola! Espero que estén teniendo un buen día",
        
        # Consultas de productos específicas
        "Quisiera saber qué tipos de milanesas tienen disponibles",
        "¿Tienen milanesas veganas o vegetarianas?",
        
        # Consultas de pedidos específicas
        "Hice un pedido ayer, ¿podrían decirme cuándo llegará?",
        "Pedido #12345 - ¿cuál es su estado?",
        
        # Consultas de horarios específicas
        "¿Están abiertos los domingos?",
        "¿Hasta qué hora atienden hoy?",
        
        # Consultas de pago específicas
        "¿Puedo pagar con tarjeta American Express?",
        "¿Tienen algún descuento si pago en efectivo?",
        
        # Mensajes ambiguos que deberían ir al asistente AI
        "No estoy seguro de qué quiero pedir",
        "¿Qué me recomiendan?",
        
        # Mensajes con múltiples intenciones
        "Hola, quiero saber si tienen milanesas de soja y si aceptan Mercado Pago",
        "¿Cuál es el horario de entrega y el costo del envío?",
        
        # Comandos numéricos del menú
        "1",  # Ver productos
        "2",  # Hacer pedido
    ]
    
    for i, message in enumerate(advanced_messages, 1):
        print(f"\n📱 MENSAJE {i}/{len(advanced_messages)}: '{message}'")
        response = simulate_whatsapp_message(message)
        print_response(response)
        time.sleep(0.5)  # Pequeña pausa entre mensajes
    
    print("\n✅ PRUEBA AVANZADA COMPLETADA ✅\n")

if __name__ == "__main__":
    run_advanced_test()
    print("Prueba finalizada. Deteniendo el servidor...")
