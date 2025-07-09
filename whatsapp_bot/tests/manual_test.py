"""
Script para pruebas manuales del bot de WhatsApp

Este script simula mensajes entrantes de WhatsApp para probar manualmente
el flujo completo del bot sin necesidad de configurar Twilio.

Uso:
    python whatsapp_bot/tests/manual_test.py
"""
import os
import sys
import json
import requests
import time

# Ajustar el path de Python para encontrar el proyecto Django
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# URL base del servidor Django local
BASE_URL = "http://127.0.0.1:8080"

def simulate_whatsapp_message(message_body):
    """
    Simula un mensaje entrante de WhatsApp.
    
    Args:
        message_body: Contenido del mensaje
        
    Returns:
        Respuesta HTTP de la solicitud
    """
    webhook_url = f"{BASE_URL}/webhook/whatsapp/"  # URL completa al servidor Django en ejecución
    
    # Datos de ejemplo para simular mensajes de WhatsApp
    whatsapp_data = {
        'From': 'whatsapp:+5491112345678',
        'Body': message_body,
        'ProfileName': 'Usuario de Prueba',
        'WaId': '5491112345678'
    }
    
    # Usar requests para enviar una solicitud HTTP real al servidor
    response = requests.post(webhook_url, data=whatsapp_data)
    return response

def print_response(response):
    """
    Imprime la respuesta de manera legible.
    
    Args:
        response: Respuesta HTTP de requests
    """
    print("\n==================================================\n")
    print(f"Status Code: {response.status_code}")
    print("\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    print("\nContent:")
    print(response.text)
    print("\n==================================================\n")

def run_test_flow(interactive=False):
    """
    Ejecuta un flujo de prueba completo con diferentes tipos de mensajes.
    
    Args:
        interactive: Si es True, pausa entre mensajes para revisión manual
    """
    print("\n🤖 INICIANDO PRUEBA MANUAL DEL BOT DE WHATSAPP 🤖\n")
    
    # Lista de mensajes de prueba
    test_messages = [
        'Hola',
        '1',  # Ver productos (opción numérica del menú)
        'Milanesas de carne',
        '3',  # Consultar estado de pedido (opción numérica del menú)
        '4',  # Ver ofertas especiales (opción numérica del menú)
        '5',  # Hablar con atención al cliente (opción numérica del menú)
        'Horarios de atención',
        'Formas de pago',
        'Mensaje confuso que debería ir al asistente AI',
        'Menu'
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📱 MENSAJE {i}/{len(test_messages)}: '{message}'")
        response = simulate_whatsapp_message(message)
        print_response(response)
        
        # Pausa para revisión manual solo en modo interactivo
        if interactive and i < len(test_messages):
            try:
                input("Presiona Enter para continuar con el siguiente mensaje...")
            except EOFError:
                print("Modo no interactivo detectado, continuando automáticamente...")
                break
    
    print("\n✅ PRUEBA MANUAL COMPLETADA ✅\n")

if __name__ == "__main__":
    run_test_flow()
