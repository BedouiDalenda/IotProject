import paho.mqtt.client as mqtt
import pandas as pd
import time
import json

# ============ CONFIGURATION ============
BROKER = "localhost"  # Ton broker Mosquitto local
PORT = 1883
TOPIC = "medical/vitals"  # Topic pour les signes vitaux
CSV_FILE = "medical_data.csv"  # Nom de ton fichier CSV
DELAY = 0.1  # Délai entre chaque envoi (100ms pour simulation temps réel)

# ============ CONNEXION MQTT ============
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connecté au broker MQTT!")
    else:
        print(f"❌ Échec de connexion, code: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect(BROKER, PORT, 60)
    client.loop_start()  # Démarre la boucle en arrière-plan
except Exception as e:
    print(f"❌ Erreur de connexion au broker: {e}")
    exit(1)

# ============ LECTURE DU CSV ============
try:
    print(f"📄 Lecture du fichier: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    df.columns = df.columns.str.strip()
    print(f"📊 {len(df)} lignes trouvées")
    print(f"📡 Colonnes disponibles: {list(df.columns)}")
except FileNotFoundError:
    print(f"❌ Fichier introuvable: {CSV_FILE}")
    exit(1)
except Exception as e:
    print(f"❌ Erreur lors de la lecture du CSV: {e}")
    exit(1)

# ============ SIMULATION CONTINUE ============
print("🚀 Simulation d'envoi de données en continu...")

try:
    while True:
        for index, row in df.iterrows():
            message = {
                "timestamp": str(row['timestamp']),
                "heart_rate": int(row['heart_rate']),
                "systolic_bp": int(row['systolic_bp']),
                "diastolic_bp": int(row['diastolic_bp']),
                "oxygen_sat": int(row['oxygen_sat']),
                "temperature": float(row['temperature'])
            }

            result = client.publish(TOPIC, json.dumps(message))

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"✅ Envoyé [{index+1}/{len(df)}]: HR={message['heart_rate']} BP={message['systolic_bp']}/{message['diastolic_bp']} O2={message['oxygen_sat']}% T={message['temperature']}°C")
            else:
                print(f"❌ Erreur d'envoi: {result.rc}")

            time.sleep(DELAY)

        # Boucle infinie : recommence le CSV depuis le début
except KeyboardInterrupt:
    print("\n🛑 Simulation interrompue par l'utilisateur")
finally:
    client.loop_stop()
    client.disconnect()
    print("👋 Déconnecté du broker")
