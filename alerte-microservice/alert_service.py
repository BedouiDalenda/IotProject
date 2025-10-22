import paho.mqtt.client as mqtt
import json
from datetime import datetime

# ============ CONFIGURATION ============
BROKER = "localhost"
PORT = 1883
TOPIC_DATA = "medical/vitals"   # Topic à écouter
TOPIC_ALERT = "medical/alerts"  # Topic pour les alertes

# Seuils pour déclencher une alerte
THRESHOLDS = {
    "heart_rate": {"max": 120, "min": 50, "unit": "BPM"},
    "systolic_bp": {"max": 140, "min": 90, "unit": "mmHg"},
    "diastolic_bp": {"max": 90, "min": 60, "unit": "mmHg"},
    "oxygen_sat": {"max": 100, "min": 92, "unit": "%"},
    "temperature": {"max": 38.0, "min": 36.0, "unit": "°C"}
}

ALERT_LEVELS = {
    "CRITIQUE": "🔴",
    "AVERTISSEMENT": "🟡",
    "INFO": "🟢"
}

# ============ CALLBACK MQTT ============
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connecté au broker MQTT pour les alertes!")
        client.subscribe(TOPIC_DATA)
        print(f"📡 Abonné au topic: {TOPIC_DATA}")
    else:
        print(f"❌ Échec de connexion, code: {rc}")

def analyze_vitals(data):
    """Analyse les signes vitaux et génère des alertes"""
    alerts = []
    
    for key, thresholds in THRESHOLDS.items():
        if key not in data:
            continue
            
        value = data[key]
        
        # Vérifier les seuils minimum
        if "min" in thresholds and value < thresholds["min"]:
            alerts.append({
                "level": "CRITIQUE",
                "vital": key,
                "value": value,
                "threshold": thresholds["min"],
                "type": "min",
                "unit": thresholds["unit"],
                "message": f"{key.replace('_', ' ').title()} trop bas: {value} {thresholds['unit']} (min: {thresholds['min']})"
            })
        
        # Vérifier les seuils maximum
        if "max" in thresholds and value > thresholds["max"]:
            alerts.append({
                "level": "CRITIQUE",
                "vital": key,
                "value": value,
                "threshold": thresholds["max"],
                "type": "max",
                "unit": thresholds["unit"],
                "message": f"{key.replace('_', ' ').title()} trop élevé: {value} {thresholds['unit']} (max: {thresholds['max']})"
            })
    
    return alerts

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        # Analyser les signes vitaux
        alerts = analyze_vitals(data)
        
        # Publier l'alerte si nécessaire
        if alerts:
            alert_message = {
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "patient_data": {
                    "heart_rate": data.get("heart_rate"),
                    "systolic_bp": data.get("systolic_bp"),
                    "diastolic_bp": data.get("diastolic_bp"),
                    "oxygen_sat": data.get("oxygen_sat"),
                    "temperature": data.get("temperature")
                },
                "alerts": alerts,
                "alert_count": len(alerts)
            }
            
            # Publier sur le topic d'alerte
            result = client.publish(TOPIC_ALERT, json.dumps(alert_message))
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"\n🚨 ALERTE DÉTECTÉE:")
                for alert in alerts:
                    print(f"   {ALERT_LEVELS[alert['level']]} {alert['message']}")
                print(f"✅ Alerte publiée sur {TOPIC_ALERT}")
            else:
                print(f"❌ Erreur publication alerte: {result.rc}")
        else:
            # Message de confirmation (optionnel, commentez si trop verbeux)
            # print(f"✓ Données normales - Pas d'alerte")
            pass

    except json.JSONDecodeError as e:
        print(f"❌ Erreur décodage JSON: {e}")
    except Exception as e:
        print(f"❌ Erreur traitement message: {e}")

# ============ CLIENT MQTT ============
print("🚀 Démarrage du microservice d'alertes...")
print(f"📊 Seuils configurés:")
for key, thresholds in THRESHOLDS.items():
    print(f"   • {key}: min={thresholds.get('min', 'N/A')} max={thresholds.get('max', 'N/A')} {thresholds['unit']}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"\n🔌 Connexion au broker {BROKER}:{PORT}...")
    client.connect(BROKER, PORT, 60)
    print("🎧 En écoute des données médicales...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\n🛑 Microservice d'alertes interrompu")
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    client.disconnect()
    print("👋 Déconnecté du broker")