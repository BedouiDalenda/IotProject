📝 Description
Système de surveillance médicale en temps réel basé sur MQTT pour la communication entre microservices. Surveille les signes vitaux (fréquence cardiaque, pression artérielle, saturation O₂, température) avec détection automatique d'anomalies et alertes.
Projet académique pour comprendre l'architecture Publish/Subscribe avec MQTT.

📦 Installation :

1️⃣ Installer Mosquitto (Broker MQTT)
Option A : Docker
bashdocker run -d -p 1883:1883 -p 9001:9001 eclipse-mosquitto
Option B : Installation locale

Windows : Télécharger
Linux : sudo apt-get install mosquitto
Mac : brew install mosquitto

2️⃣ Installer les dépendances Python
bashpip install -r requirements.txt

3️⃣ Installer les dépendances Node.js
bashcd ecg-microservice
npm init -y
npm install mqtt express ws

▶️ Utilisation
Étape 1 : Démarrer le Broker MQTT

bash # Si Docker
docker start <container_id>

bash # Si local
mosquitto -c mosquitto.conf

Étape 2 : Générer les données médicales
bashpython generate_medical_data.py

✅ Crée medical_data_realistic.csv

Étape 3 : Lancer le microservice d'alertes
bashcd alerte-microservice
python alert_service.py
🚨 En écoute sur medical/vitals, publie sur medical/alerts

Étape 4 : Lancer le serveur WebSocket
bashcd ecg-microservice
node server.js
🌐 WebSocket : ws://localhost:3000

Étape 5 : Ouvrir le Dashboard
Ouvrir index.html dans un navigateur

Étape 6 : Publier les données
bashcd publisher
python publisher.py
