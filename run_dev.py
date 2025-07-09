#!/usr/bin/env python
"""
Script de desarrollo para breaders_twilio_bot

Este script configura un entorno de desarrollo local para el bot de WhatsApp:
1. Inicia un túnel ngrok para exponer el servidor local a Internet
2. Actualiza la configuración de Django con la URL de ngrok
3. Inicia el servidor de desarrollo de Django
4. Proporciona información para configurar los webhooks de Twilio

Uso:
    python run_dev.py
    python run_dev.py --stop  # Para detener todos los procesos en ejecución
"""
import os
import sys
import json
import time
import signal
import socket
import threading
import subprocess
import requests
import argparse
from urllib.parse import urlparse
from django.conf import settings
from django.core.management import call_command

# Evento para señalizar que ngrok está listo
ngrok_ready_event = threading.Event()

# Lista para mantener referencia a los procesos
processes = []

def close_all_processes():
    """Cierra todos los procesos de forma ordenada, incluyendo ngrok"""
    print("\n🛑️ Cerrando todos los procesos...")
    
    # Primero intentamos cerrar los procesos que tenemos registrados
    for process in processes:
        try:
            print(f"🔄 Terminando proceso: {process.args[0] if hasattr(process, 'args') else 'desconocido'}")
            process.terminate()
            process.wait(timeout=5)
        except Exception as e:
            print(f"⚠️ Error al cerrar proceso: {e}")
    
    # Asegurarnos de que ngrok se cierre correctamente
    try:
        print("🔄 Buscando procesos de ngrok...")
        ngrok_pids = subprocess.run(
            ["pgrep", "-f", "ngrok http"],
            capture_output=True, 
            text=True
        ).stdout.strip().split('\n')
        
        for pid in ngrok_pids:
            if pid:
                print(f"🔄 Terminando ngrok (PID: {pid})...")
                subprocess.run(["kill", pid])
    except Exception as e:
        print(f"⚠️ Error al buscar/terminar ngrok: {e}")
    
    # Asegurarnos de que Django runserver se cierre correctamente
    try:
        print("🔄 Buscando procesos de Django runserver...")
        django_pids = subprocess.run(
            ["pgrep", "-f", "runserver"],
            capture_output=True, 
            text=True
        ).stdout.strip().split('\n')
        
        for pid in django_pids:
            if pid:
                print(f"🔄 Terminando Django runserver (PID: {pid})...")
                subprocess.run(["kill", pid])
    except Exception as e:
        print(f"⚠️ Error al buscar/terminar Django runserver: {e}")
    
    # Eliminar archivos temporales de ngrok
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ngrok_host_file = os.path.join(base_dir, 'ngrok_host.txt')
        ngrok_url_file = os.path.join(base_dir, 'ngrok_url.txt')
        
        if os.path.exists(ngrok_host_file):
            os.remove(ngrok_host_file)
            print("🔄 Archivo temporal ngrok_host.txt eliminado")
            
        if os.path.exists(ngrok_url_file):
            os.remove(ngrok_url_file)
            print("🔄 Archivo temporal ngrok_url.txt eliminado")
    except Exception as e:
        print(f"⚠️ Error al eliminar archivos temporales de ngrok: {e}")
    
    print("✅ Todos los procesos han sido cerrados.")

def signal_handler(sig, frame):
    """Manejador de señales para cierre ordenado"""
    close_all_processes()
    sys.exit(0)

def setup_django():
    """Configura Django para ser usado fuera de un entorno web"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'breaders_twilio_bot.settings')
    import django
    django.setup()
    from django.conf import settings
    return settings

def check_port_in_use(port):
    """Verifica si un puerto está en uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port(start_port=8000, max_attempts=10):
    """Encuentra un puerto libre a partir de start_port"""
    port = start_port
    attempts = 0
    
    while check_port_in_use(port) and attempts < max_attempts:
        port += 1
        attempts += 1
    
    if attempts >= max_attempts:
        raise Exception(f"No se pudo encontrar un puerto libre después de {max_attempts} intentos")
    
    return port

def kill_process_on_port(port):
    """Intenta matar el proceso que está usando un puerto específico"""
    try:
        # Obtener el PID del proceso que usa el puerto
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-t"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 or not result.stdout.strip():
            return False
        
        pid = result.stdout.strip()
        print(f"🔄 Intentando terminar proceso en puerto {port} (PID: {pid})...")
        
        # Intentar matar el proceso
        kill_result = subprocess.run(["kill", pid])
        
        # Verificar si el puerto ahora está libre
        time.sleep(1)  # Dar tiempo para que el proceso termine
        return not check_port_in_use(port)
    except Exception as e:
        print(f"⚠️ Error al intentar liberar el puerto {port}: {e}")
        return False

def check_port_and_handle(default_port=8000):
    """Verifica si el puerto por defecto está en uso y maneja la situación"""
    if check_port_in_use(default_port):
        print(f"⚠️ El puerto {default_port} ya está en uso")
        
        # Intentar matar el proceso
        if kill_process_on_port(default_port):
            print(f"✅ Puerto {default_port} liberado exitosamente")
            return default_port
        
        # Si no se pudo matar, buscar un puerto alternativo
        print(f"🔄 Buscando un puerto alternativo...")
        alt_port = find_free_port(default_port + 1)
        print(f"✅ Puerto alternativo encontrado: {alt_port}")
        return alt_port
    
    return default_port

def run_django():
    """Ejecuta el servidor de desarrollo estándar de Django (runserver)"""
    try:
        # Ejecutar migraciones primero
        print("🔄 Ejecutando migraciones de Django...")
        migrate_process = subprocess.run(
            [sys.executable, 'manage.py', 'migrate'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if migrate_process.returncode != 0:
            print("⚠️ Advertencia: Las migraciones no se completaron correctamente")
        else:
            print("✅ Migraciones completadas")
        
        # Verificar si el puerto 8000 está en uso
        port = check_port_and_handle()
        
        # Iniciar el servidor de desarrollo de Django
        print(f"🚀 Iniciando servidor Django en el puerto {port}...")
        django_process = subprocess.Popen(
            [sys.executable, 'manage.py', 'runserver', f'0.0.0.0:{port}'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        processes.append(django_process)
        
        print(f"✅ Servidor Django iniciado en http://localhost:{port}/")
        print("\nAcceso a la administración de Django:")
        print(f"  → http://localhost:{port}/admin/")
        print("\nEndpoint de webhook de WhatsApp:")
        print(f"  → http://localhost:{port}/webhook/whatsapp/")
        
        # Mantener el proceso principal en ejecución
        django_process.wait()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error al iniciar Django: {e}")
        print("\nPor favor, verifica la configuración de tu proyecto Django.")
        sys.exit(1)

def update_twilio_webhook(ngrok_url):
    """
    Actualiza el webhook de Twilio con la URL de ngrok
    
    Args:
        ngrok_url: URL pública de ngrok
    """
    try:
        # Cargar configuración de Twilio
        settings = setup_django()
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        if not account_sid or not auth_token:
            print("⚠️ No se encontraron credenciales de Twilio en la configuración")
            print("ℹ️ Configura manualmente el webhook de Twilio con la siguiente URL:")
            print(f"   {ngrok_url}/webhook/whatsapp/")
            return
        
        # Construir la URL del webhook (nota: cambiado a /webhook/whatsapp/ para coincidir con las URLs de Django)
        webhook_url = f"{ngrok_url}/webhook/whatsapp/"
        
        print(f"🔄 Actualizando webhook de Twilio a: {webhook_url}")
        
        try:
            # Intentar actualizar el webhook automáticamente usando la API de Twilio
            from twilio.rest import Client
            client = Client(account_sid, auth_token)
            
            # Buscar números de WhatsApp asociados a la cuenta
            incoming_phone_numbers = client.incoming_phone_numbers.list()
            whatsapp_numbers = []
            
            for number in incoming_phone_numbers:
                if 'whatsapp' in number.friendly_name.lower():
                    whatsapp_numbers.append(number)
            
            if whatsapp_numbers:
                for number in whatsapp_numbers:
                    print(f"🔄 Actualizando webhook para {number.friendly_name}...")
                    number.update(
                        sms_url=webhook_url,
                        sms_method='POST'
                    )
                print("✅ Webhooks de Twilio actualizados automáticamente")
            else:
                # Si no se encuentran números de WhatsApp, mostrar instrucciones manuales
                print("⚠️ No se encontraron números de WhatsApp configurados")
                print("ℹ️ Para configurar el webhook de Twilio manualmente:")
                print(f"   1. Ve a https://www.twilio.com/console/sms/whatsapp/sandbox")
                print(f"   2. En 'When a message comes in', configura esta URL: {webhook_url}")
                print(f"   3. Asegúrate de seleccionar HTTP POST como método")
        except ImportError:
            print("⚠️ No se pudo importar el cliente de Twilio. Instalando...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'twilio'])
            print("ℹ️ Por favor, configura el webhook manualmente:")
            print(f"   1. Ve a https://www.twilio.com/console/sms/whatsapp/sandbox")
            print(f"   2. En 'When a message comes in', configura esta URL: {webhook_url}")
            print(f"   3. Asegúrate de seleccionar HTTP POST como método")
        except Exception as e:
            print(f"⚠️ Error al actualizar webhook automáticamente: {e}")
            print("ℹ️ Por favor, configura el webhook manualmente:")
            print(f"   1. Ve a https://www.twilio.com/console/sms/whatsapp/sandbox")
            print(f"   2. En 'When a message comes in', configura esta URL: {webhook_url}")
            print(f"   3. Asegúrate de seleccionar HTTP POST como método")
    except Exception as e:
        print(f"❌ Error al actualizar webhook de Twilio: {e}")
        print("ℹ️ Por favor, configura el webhook manualmente:")
        print(f"   1. Ve a https://www.twilio.com/console/sms/whatsapp/sandbox")
        print(f"   2. En 'When a message comes in', configura esta URL: {ngrok_url}/webhook/whatsapp/")
        print(f"   3. Asegúrate de seleccionar HTTP POST como método")

def run_ngrok():
    """Ejecuta ngrok y actualiza la configuración de Django con la nueva URL"""
    # Verificar si ngrok ya está en ejecución
    try:
        check_ngrok = subprocess.run(
            ['pgrep', '-f', 'ngrok http'],
            capture_output=True,
            text=True
        )
        if check_ngrok.stdout.strip():
            print("⚠️ ngrok ya está en ejecución. Terminando proceso anterior...")
            subprocess.run(['pkill', '-f', 'ngrok http'])
            time.sleep(2)  # Dar más tiempo para que termine
    except Exception as e:
        print(f"ℹ️ No se pudo verificar si ngrok está en ejecución: {e}")
    
    # Verificar si ngrok está instalado
    try:
        subprocess.run(['which', 'ngrok'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ ngrok no está instalado. Por favor, instálalo desde https://ngrok.com/download")
        ngrok_ready_event.set()  # Señalizar para continuar con el flujo
        return
    
    # Iniciar ngrok con parámetros mejorados
    print("🚀 Iniciando túnel ngrok...")
    try:
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', '8000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        processes.append(ngrok_process)
    except Exception as e:
        print(f"❌ Error al iniciar ngrok: {e}")
        print("Continuando sin ngrok. El servidor solo será accesible localmente.")
        ngrok_ready_event.set()
        return
    
    # Dar a ngrok tiempo suficiente para iniciar
    print("⏳ Esperando a que ngrok inicie completamente...")
    time.sleep(5)  # Aumentar el tiempo de espera inicial
    
    # Intentar obtener información del túnel con reintentos
    max_retries = 5  # Aumentar el número de reintentos
    retry_count = 0
    tunnel_found = False
    wait_time = 2  # Tiempo inicial de espera entre reintentos
    
    while not tunnel_found and retry_count < max_retries:
        try:
            print(f"🔄 Obteniendo información del túnel ngrok (intento {retry_count + 1}/{max_retries})...")
            # Intentar acceder directamente a la API de túneles con seguimiento de redirecciones
            print(f"🔄 Intentando acceder a la API de ngrok...")
            
            # Usar -L para seguir redirecciones
            ngrok_api = subprocess.run(
                ['curl', '-s', '-L', 'http://localhost:4040/api/tunnels'],
                capture_output=True,
                text=True
            )
            
            # Verificar que la respuesta no esté vacía
            if not ngrok_api.stdout.strip():
                print("⚠️ Respuesta vacía de la API de ngrok, reintentando...")
                retry_count += 1
                time.sleep(wait_time)
                wait_time += 1
                continue
                
            tunnels = json.loads(ngrok_api.stdout)
            
            if not tunnels.get('tunnels'):
                print("⚠️ No se encontraron túneles en la respuesta de ngrok, reintentando...")
                retry_count += 1
                time.sleep(wait_time)
                wait_time += 1
                continue
            
            for tunnel in tunnels.get('tunnels', []):
                if tunnel['proto'] == 'https':
                    ngrok_url = tunnel['public_url']
                    hostname = ngrok_url.replace('https://', '')
                
                    # Actualizar ALLOWED_HOSTS
                    settings = setup_django()
                    if hostname not in settings.ALLOWED_HOSTS:
                        settings.ALLOWED_HOSTS.append(hostname)
                    
                    # Guardar la información de ngrok en archivos y variables de entorno
                    # para que sea accesible por la configuración de Django
                    try:
                        # Guardar en archivos temporales
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        with open(os.path.join(base_dir, 'ngrok_host.txt'), 'w') as f:
                            f.write(hostname)
                        with open(os.path.join(base_dir, 'ngrok_url.txt'), 'w') as f:
                            f.write(ngrok_url)
                        
                        # Establecer variables de entorno
                        os.environ['NGROK_HOST'] = hostname
                        os.environ['NGROK_URL'] = ngrok_url
                        
                        print(f"✅ Información de ngrok guardada para uso de Django")
                    except Exception as e:
                        print(f"⚠️ Error al guardar información de ngrok: {e}")
                    
                    print(f"✅ Django ahora es accesible en {ngrok_url}")
                    print(f"🔄 Actualizando configuración de Django con nuevo hostname: {hostname}")
                    
                    # Actualizar webhook de Twilio
                    update_twilio_webhook(ngrok_url)
                    
                    # Señalizar que ngrok está listo
                    ngrok_ready_event.set()
                    tunnel_found = True
                    break
            
            if not tunnel_found:
                print("⚠️ No se encontró túnel HTTPS de ngrok, reintentando...")
                retry_count += 1
                time.sleep(wait_time)
                wait_time += 1
        except json.JSONDecodeError as e:
            print(f"⚠️ Error al decodificar JSON de ngrok (intento {retry_count + 1}): {e}")
            print(f"Respuesta recibida: '{ngrok_api.stdout[:100]}...'" if len(ngrok_api.stdout) > 100 else f"Respuesta recibida: '{ngrok_api.stdout}'")
            retry_count += 1
            time.sleep(wait_time)
            wait_time += 1
        except Exception as e:
            print(f"⚠️ Error al obtener URL de ngrok (intento {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(wait_time)
            wait_time += 1
    
    if not tunnel_found:
        print("❌ No se pudo obtener la URL de ngrok después de varios intentos")
        print("El servidor solo será accesible localmente en http://localhost:8000/")
        # Señalizar que la configuración de ngrok está completa incluso si hubo un error
        ngrok_ready_event.set()
    
    # Mantener ngrok en ejecución
    try:
        ngrok_process.wait()
    except KeyboardInterrupt:
        pass

def print_welcome_message():
    """Imprime un mensaje de bienvenida con instrucciones"""
    print("\n" + "="*80)
    print("🤖 BREADERS TWILIO BOT - ENTORNO DE DESARROLLO 🤖".center(80))
    print("="*80)
    print("\nEste script configura un entorno de desarrollo local para el bot de WhatsApp:")
    print("1. 🔥 Inicia un túnel ngrok para exponer el servidor local a Internet")
    print("2. 🔄 Actualiza la configuración de Django con la URL de ngrok")
    print("3. 🚀 Inicia el servidor de desarrollo de Django")
    print("4. 📞 Actualiza automáticamente los webhooks de Twilio cuando es posible")
    print("5. 📈 Ejecuta migraciones de la base de datos")
    print("\nComandos:")
    print("- python3 run_dev.py         ➡️ Inicia el entorno de desarrollo")
    print("- python3 run_dev.py --stop  ➡️ Detiene todos los procesos")
    print("\nPresiona Ctrl+C para detener todos los procesos")
    print("="*80 + "\n")

def check_dependencies():
    """Verifica e instala las dependencias necesarias"""
    dependencies = ['twilio', 'django']
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            print(f"⚠️ {dep} no está instalado. Instalando...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', dep])

if __name__ == "__main__":
    # Procesar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description="Script de desarrollo para breaders_twilio_bot")
    parser.add_argument('--stop', action='store_true', help='Detener todos los procesos en ejecución')
    parser.add_argument('--check', action='store_true', help='Verificar dependencias y salir')
    args = parser.parse_args()
    
    # Si se solicita detener los procesos, hacerlo y salir
    if args.stop:
        close_all_processes()
        sys.exit(0)
    
    # Si se solicita verificar dependencias, hacerlo y salir
    if args.check:
        check_dependencies()
        sys.exit(0)
    
    # Configurar manejador de señales para cierre ordenado
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Imprimir mensaje de bienvenida
    print_welcome_message()
    
    # Verificar dependencias
    check_dependencies()
    
    # Configurar Django
    settings = setup_django()
    
    # Iniciar ngrok en un hilo separado
    ngrok_thread = threading.Thread(target=run_ngrok)
    ngrok_thread.daemon = True
    ngrok_thread.start()
    
    # Esperar a que ngrok esté listo antes de iniciar Django
    print("⏳ Esperando a que ngrok se configure completamente...")
    ngrok_ready_event.wait(timeout=30)  # Esperar hasta 30 segundos a que ngrok esté listo
    
    if ngrok_ready_event.is_set():
        print("✅ Ngrok está listo, iniciando servidor Django...")
        print("")
        print("="*80)
        print("")
    else:
        print("⚠️ Tiempo de espera agotado esperando a que ngrok se configure. Iniciando Django de todos modos...")
        print("")
        print("="*80)
        print("")
    
    # Ejecutar Django en el hilo principal
    run_django()
