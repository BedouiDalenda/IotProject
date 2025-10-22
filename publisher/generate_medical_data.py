# generate_medical_data.py
import csv
import random
from datetime import datetime, timedelta

def generate_realistic_medical_data(num_records=200):
    """Génère des données médicales réalistes avec peu d'alertes"""
    
    data = []
    base_time = datetime.now().replace(hour=2, minute=4, second=44)
    
    for i in range(num_records):
        # 85% de données normales
        if random.random() < 0.85:
            heart_rate = random.randint(65, 85)
            systolic_bp = random.randint(110, 130)
            diastolic_bp = random.randint(70, 85)
            oxygen_sat = random.randint(96, 99)
            temperature = round(random.uniform(36.5, 37.2), 1)
        
        # 10% de légères variations
        elif random.random() < 0.95:
            heart_rate = random.randint(60, 100)
            systolic_bp = random.randint(100, 140)
            diastolic_bp = random.randint(65, 90)
            oxygen_sat = random.randint(94, 96)
            temperature = round(random.uniform(36.2, 37.5), 1)
        
        # 5% d'alertes seulement
        else:
            # Quelques cas d'alertes variées
            alert_type = random.choice(["high_hr", "low_bp", "high_temp", "low_o2"])
            
            if alert_type == "high_hr":
                heart_rate = random.randint(130, 150)
                systolic_bp = random.randint(110, 130)
                diastolic_bp = random.randint(70, 85)
                oxygen_sat = random.randint(96, 99)
                temperature = round(random.uniform(36.5, 37.2), 1)
            
            elif alert_type == "low_bp":
                heart_rate = random.randint(65, 85)
                systolic_bp = random.randint(85, 95)
                diastolic_bp = random.randint(50, 60)
                oxygen_sat = random.randint(96, 99)
                temperature = round(random.uniform(36.5, 37.2), 1)
            
            elif alert_type == "high_temp":
                heart_rate = random.randint(65, 85)
                systolic_bp = random.randint(110, 130)
                diastolic_bp = random.randint(70, 85)
                oxygen_sat = random.randint(96, 99)
                temperature = round(random.uniform(38.3, 38.8), 1)
            
            elif alert_type == "low_o2":
                heart_rate = random.randint(65, 85)
                systolic_bp = random.randint(110, 130)
                diastolic_bp = random.randint(70, 85)
                oxygen_sat = random.randint(88, 91)
                temperature = round(random.uniform(36.5, 37.2), 1)
        
        timestamp = (base_time + timedelta(seconds=i)).strftime("%H:%M:%S")
        
        data.append([
            timestamp,
            heart_rate,
            systolic_bp,
            diastolic_bp,
            oxygen_sat,
            temperature
        ])
    
    return data

def save_to_csv(data, filename="medical_data_realistic.csv"):
    """Sauvegarde les données en CSV"""
    headers = ["timestamp", "heart_rate", "systolic_bp", "diastolic_bp", "oxygen_sat", "temperature"]
    
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    
    print(f"✅ Données sauvegardées dans {filename}")
    print(f"📊 {len(data)} enregistrements générés")

if __name__ == "__main__":
    # Générer 200 points de données réalistes
    medical_data = generate_realistic_medical_data(200)
    save_to_csv(medical_data)
    
    # Afficher un aperçu
    print("\n📋 Aperçu des données:")
    for i, row in enumerate(medical_data[:10]):
        print(f"  {row}")