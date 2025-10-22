const mqtt = require('mqtt');
const express = require('express');
const WebSocket = require('ws');
const http = require('http');

// ============ CONFIGURATION ============
const MQTT_BROKER = 'mqtt://localhost:1883';
const TOPIC_VITALS = 'medical/vitals';
const TOPIC_ALERTS = 'medical/alerts';
const HTTP_PORT = 3000;

// ============ EXPRESS APP ============
const app = express();
const server = http.createServer(app);

// ============ WEBSOCKET SERVER ============
const wss = new WebSocket.Server({ server });

// ============ MQTT CLIENT (SUBSCRIBER) ============
console.log('🔌 Connexion au broker MQTT...');
const mqttClient = mqtt.connect(MQTT_BROKER);

mqttClient.on('connect', () => {
    console.log('✅ Connecté au broker MQTT!');
    
    // S'abonner aux données vitales
    mqttClient.subscribe(TOPIC_VITALS, (err) => {
        if (!err) {
            console.log(`📡 Abonné au topic: ${TOPIC_VITALS}`);
        } else {
            console.error('❌ Erreur d\'abonnement vitals:', err);
        }
    });
    
    // S'abonner aux alertes
    mqttClient.subscribe(TOPIC_ALERTS, (err) => {
        if (!err) {
            console.log(`🚨 Abonné au topic: ${TOPIC_ALERTS}`);
        } else {
            console.error('❌ Erreur d\'abonnement alerts:', err);
        }
    });
});

mqttClient.on('error', (error) => {
    console.error('❌ Erreur MQTT:', error);
});

// ============ WEBSOCKET CONNECTION MANAGEMENT ============
console.log(`🌐 WebSocket server démarré sur le port ${HTTP_PORT}`);

let connectedClients = 0;
let stats = {
    vitals_received: 0,
    alerts_received: 0,
    messages_sent: 0
};

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
    
    // Envoyer un message de bienvenue
    ws.send(JSON.stringify({
        type: 'connection',
        message: 'Connecté au serveur de surveillance médicale',
        timestamp: new Date().toISOString()
    }));
});

// ============ FONCTION D'ENVOI AUX CLIENTS ============
function broadcastToClients(data) {
    let sentCount = 0;
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(data));
            sentCount++;
            stats.messages_sent++;
        }
    });
    return sentCount;
}

// ============ LISTENER MQTT → WEBSOCKET ============
mqttClient.on('message', (topic, message) => {
    try {
        const data = JSON.parse(message.toString());
        
        if (topic === TOPIC_VITALS) {
            // Données vitales
            stats.vitals_received++;
            console.log(`📊 Vitals: HR=${data.heart_rate} BP=${data.systolic_bp}/${data.diastolic_bp} O2=${data.oxygen_sat}% T=${data.temperature}°C`);
            
            const payload = {
                type: 'vitals',
                data: data
            };
            
            const sent = broadcastToClients(payload);
            if (sent > 0) {
                console.log(`✅ Vitals envoyés à ${sent} client(s)`);
            }
        } 
        else if (topic === TOPIC_ALERTS) {
            // Alertes
            stats.alerts_received++;
            console.log(`🚨 ALERTE: ${data.alert_count} alerte(s) détectée(s)`);
            
            const payload = {
                type: 'alert',
                data: data
            };
            
            const sent = broadcastToClients(payload);
            if (sent > 0) {
                console.log(`✅ Alerte envoyée à ${sent} client(s)`);
            }
        }
    } catch (error) {
        console.error('❌ Erreur de traitement:', error);
    }
});

// ============ HTTP SERVER (API) ============
app.use(express.static('public'));

app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        mqtt_connected: mqttClient.connected,
        websocket_clients: connectedClients,
        stats: stats,
        timestamp: new Date().toISOString()
    });
});

app.get('/stats', (req, res) => {
    res.json({
        clients: connectedClients,
        vitals_received: stats.vitals_received,
        alerts_received: stats.alerts_received,
        messages_sent: stats.messages_sent,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
    });
});

server.listen(HTTP_PORT, () => {
    console.log(`\n🚀 Serveur HTTP + WebSocket démarré`);
    console.log(`   📍 URL: http://localhost:${HTTP_PORT}`);
    console.log(`   💡 Health check: http://localhost:${HTTP_PORT}/health`);
    console.log(`   📊 Stats: http://localhost:${HTTP_PORT}/stats`);
    console.log(`\n⏳ En attente de connexions...\n`);
});

// ============ GESTION DE L'ARRÊT ============
process.on('SIGINT', () => {
    console.log('\n\n📊 Statistiques finales:');
    console.log(`   • Vitals reçus: ${stats.vitals_received}`);
    console.log(`   • Alertes reçues: ${stats.alerts_received}`);
    console.log(`   • Messages envoyés: ${stats.messages_sent}`);
    console.log('\n👋 Arrêt du serveur...');
    mqttClient.end();
    wss.close();
    server.close();
    process.exit();
});