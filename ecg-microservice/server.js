const mqtt = require('mqtt');
const express = require('express');
const WebSocket = require('ws');
const http = require('http');

// ============ CONFIGURATION ============
const MQTT_BROKER = 'mqtt://localhost:1883';
const MQTT_TOPIC = 'ecg/data';
const HTTP_PORT = 3000;


// ============ EXPRESS APP ============
const app = express(); // 💡 Crée l'app AVANT de l'utiliser dans http.createServer
const server = http.createServer(app); // 💡 OK maintenant

// ============ WEBSOCKET SERVER ============
const wss = new WebSocket.Server({ server });

// ============ MQTT CLIENT (SUBSCRIBER) ============
console.log('🔌 Connexion au broker MQTT...');
const mqttClient = mqtt.connect(MQTT_BROKER);

mqttClient.on('connect', () => {
    console.log('✅ Connecté au broker MQTT!');
    mqttClient.subscribe(MQTT_TOPIC, (err) => {
        if (!err) {
            console.log(`📡 Abonné au topic: ${MQTT_TOPIC}`);
        } else {
            console.error('❌ Erreur d\'abonnement:', err);
        }
    });
});

mqttClient.on('error', (error) => {
    console.error('❌ Erreur MQTT:', error);
});

// ============ WEBSOCKET/HTTP SERVER ============

console.log(`🌐 WebSocket server démarré sur le port ${HTTP_PORT}`);

let connectedClients = 0;

wss.on('connection', (ws) => {
    connectedClients++;
    console.log(`👤 Nouveau client connecté (Total: ${connectedClients})`);

    ws.on('close', () => {
        connectedClients--;
        console.log(`👋 Client déconnecté (Total: ${connectedClients})`);
    });

    ws.on('error', (error) => {
        console.error('❌ Erreur WebSocket:', error);
    });
});

// ============ LISTENER MQTT → WEBSOCKET ============
mqttClient.on('message', (topic, message) => {
    try {
        const data = JSON.parse(message.toString());
        console.log(`📊 Données reçues: ${JSON.stringify(data)}`);

        // Envoyer à tous les clients WebSocket connectés
        let sentCount = 0;
        wss.clients.forEach((client) => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify(data));
                sentCount++;
            }
        });

        if (sentCount > 0) {
            console.log(`✅ Envoyé à ${sentCount} client(s)`);
        }
    } catch (error) {
        console.error('❌ Erreur de traitement:', error);
    }
});

// ============ HTTP SERVER (API optionnelle) ============

app.use(express.static('public')); // Servir les fichiers statiques (pour l'étape 3)

app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        mqtt_connected: mqttClient.connected,
        websocket_clients: connectedClients,
        timestamp: new Date().toISOString()
    });
});

server.listen(HTTP_PORT, () => {
    console.log(`🚀 Serveur HTTP + WebSocket démarré sur http://localhost:${HTTP_PORT}`);
    console.log(`💡 Health check: http://localhost:${HTTP_PORT}/health`);
});


// ============ GESTION DE L'ARRÊT ============
process.on('SIGINT', () => {
    console.log('\n👋 Arrêt du serveur...');
    mqttClient.end();
    wss.close();
    process.exit();
});