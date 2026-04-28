[README-infrastructure.md](https://github.com/user-attachments/files/27180113/README-infrastructure.md)
# Infrastructure — Abderahman's Setup Guide

## Prérequis
- Docker Desktop installé et en cours d'exécution
- Python 3.8+ (pour le simulateur)
- `pip install paho-mqtt`

---

## Démarrage en 3 commandes

```bash
# 1. Copier les variables d'environnement
cp .env.example .env

# 2. Lancer toute l'infrastructure
docker-compose up -d mosquitto influxdb

# 3. Lancer le simulateur (dans un autre terminal)
cd simulator
python sensor_sim.py
```

---

## Vérification

| Service    | URL / Port              | Vérification                          |
|------------|-------------------------|---------------------------------------|
| Mosquitto  | `localhost:1883`        | Le simulateur se connecte sans erreur |
| InfluxDB   | `http://localhost:8086` | Interface web → login admin           |
| Simulateur | Terminal                | Affiche pression + température en live|

### Tester le broker MQTT manuellement
```bash
# Dans un terminal séparé — écouter tous les messages
docker exec -it gpl_mosquitto mosquitto_sub -t "tank/#" -v
```

### Connexion InfluxDB
- URL : http://localhost:8086
- Username : `admin`
- Password : `adminpassword123`
- Organization : `naftal`
- Bucket : `gpl_metrics`

---

## Structure des messages MQTT

Le simulateur publie sur `tank/sphere1/data` au format JSON :

```json
{
  "sphere_id":  "sphere1",
  "metric":     "pressure",
  "value":      152.30,
  "unit":       "bar",
  "timestamp":  "2026-04-26T10:00:00Z"
}
```

```json
{
  "sphere_id":  "sphere1",
  "metric":     "temperature",
  "value":      28.50,
  "unit":       "°C",
  "timestamp":  "2026-04-26T10:00:02Z"
}
```

---

## Seuils normaux (pour les tests d'alerte)

| Métrique    | Min    | Max    |
|-------------|--------|--------|
| Pression    | 140 bar| 165 bar|
| Température | 18 °C  | 45 °C  |

Le simulateur génère automatiquement des **pics hors seuil** (5% des lectures)
pour tester le système d'alerte d'Aymen.

---

## Ce que tu dois livrer à l'équipe avant le 22 avril

- [ ] `docker-compose.yml` fonctionnel (mosquitto + influxdb)
- [ ] `mosquitto/mosquitto.conf` validé
- [ ] `simulator/sensor_sim.py` qui publie des données en continu
- [ ] `.env.example` partagé avec l'équipe
- [ ] Confirm à Aymen : broker MQTT accessible sur `localhost:1883`
- [ ] Confirm à Aymen : InfluxDB accessible sur `http://localhost:8086` avec le token
