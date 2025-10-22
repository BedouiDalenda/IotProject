import paho.mqtt.client as mqtt
import pandas as pd
import time
import json

# ============ CONFIGURATION ============
BROKER = "localhost"  # Ton broker Mosquitto local
PORT = 1883
TOPIC = "ecg/data"
CSV_FILE = "ecg_data.csv"  # Chemin vers ton fichier CSV
DELAY = 0.01  # Délai entre chaque envoi (en secondes) - simule le temps réel

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

# ============ LECTURE ET PUBLICATION DU CSV ============
try:
    # Lire le fichier CSV
    print(f"📄 Lecture du fichier: {CSV_FILE}")
    df = pd.read_csv(CSV_FILE)
    
    print(f"📊 {len(df)} lignes trouvées")
    print(f"📡 Colonnes disponibles: {list(df.columns)}")
    print(f"🚀 Début de l'envoi des données...\n")
    
    # Parcourir chaque ligne du CSV
    for index, row in df.iterrows():
        # Créer le message JSON
        message = {
            "timestamp": str(row.get('timestamp', index)),  # Utilise index si pas de colonne timestamp
            "ecg_value": float(row.iloc[1]) if len(row) > 1 else float(row.iloc[0])  # Prend la 2ème colonne ou la 1ère
        }
        
        # Publier sur MQTT
        result = client.publish(TOPIC, json.dumps(message))
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ Envoyé [{index+1}/{len(df)}]: {message}")
        else:
            print(f"❌ Erreur d'envoi: {result.rc}")
        
        # Attendre avant d'envoyer la prochaine valeur (simulation temps réel)
        time.sleep(DELAY)
    
    print("\n🎉 Tous les messages ont été envoyés!")

except FileNotFoundError:
    print(f"❌ Fichier introuvable: {CSV_FILE}")
    print("💡 Assure-toi que le fichier CSV est dans le même dossier que ce script")
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    print("👋 Déconnecté du broker")