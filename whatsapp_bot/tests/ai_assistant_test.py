#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test específico para el asistente AI del bot de WhatsApp de Breaders.
Este script envía consultas complejas que deberían ser manejadas por el asistente AI.
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

def run_ai_assistant_test():
    """
    Ejecuta pruebas específicas para el asistente AI con consultas complejas.
    """
    print("\n🤖 INICIANDO PRUEBA DEL ASISTENTE AI DEL BOT DE WHATSAPP 🤖\n")
    
    # Lista de mensajes complejos que deberían ir al asistente AI
    complex_messages = [
        # Consultas familiares
        "Tengo una familia de 5 personas, ¿qué me recomendás?",
        "¿Qué cantidad debería pedir para 8 personas?",
        
        # Consultas dietéticas específicas
        "¿Tienen opciones para veganos?",
        "Soy celíaco, ¿qué puedo comer?",
        "¿Las milanesas de soja son aptas para vegetarianos?",
        
        # Consultas de recomendación
        "¿Cuál es la especialidad de la casa?",
        "¿Qué milanesa es la más vendida?",
        
        # Consultas de preparación
        "¿Cómo se preparan las milanesas?",
        "¿Vienen listas para cocinar o hay que prepararlas?",
        
        # Consultas mixtas y complejas
        "Necesito milanesas para una fiesta de cumpleaños de 15 personas, ¿qué me recomiendan y cuánto saldría?",
        "¿Las milanesas veganas tienen el mismo precio que las normales? ¿Y son igual de grandes?",
        
        # Consultas de disponibilidad
        "¿Tienen stock de milanesas de berenjena?",
        "¿Para cuándo podrían tener listo un pedido grande?"
    ]
    
    for i, message in enumerate(complex_messages, 1):
        print(f"\n📱 MENSAJE {i}/{len(complex_messages)}: '{message}'")
        response = simulate_whatsapp_message(message)
        print_response(response)
        time.sleep(0.5)  # Pequeña pausa entre mensajes
    
    print("\n✅ PRUEBA DEL ASISTENTE AI COMPLETADA ✅\n")

if __name__ == "__main__":
    run_ai_assistant_test()
    print("Prueba finalizada. Deteniendo el servidor...")
