"""
sensor_sim.py — Simulateur de capteurs GPL
==========================================
Projet : Surveillance Sphère GPL — District NAFTAL Batna
Auteur : Benmohammed Abderahman (Infrastructure)

Ce script simule les capteurs de pression et de température
d'une sphère GPL et publie les données sur le broker MQTT.

Usage :
    pip install paho-mqtt
    python sensor_sim.py

Topics MQTT publiés :
    tank/sphere1/data  →  {"metric": "pressure", "value": 152.3, "unit": "bar", "timestamp": "..."}
    tank/sphere1/data  →  {"metric": "temperature", "value": 28.5, "unit": "°C", "timestamp": "..."}
"""

import json
import time
import random
import math
import datetime
import paho.mqtt.client as mqtt

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
BROKER_HOST = "localhost"   # Change to "mosquitto" if running inside Docker
BROKER_PORT = 1883
SPHERE_ID   = "sphere1"
TOPIC       = f"tank/{SPHERE_ID}/data"
INTERVAL    = 2             # seconds between each publish

# ─────────────────────────────────────────
# Normal operating ranges (from NAFTAL specs)
# ─────────────────────────────────────────
PRESSURE_NORMAL_MIN  = 140.0   # bar
PRESSURE_NORMAL_MAX  = 165.0   # bar
TEMP_NORMAL_MIN      =  18.0   # °C
TEMP_NORMAL_MAX      =  45.0   # °C

# ─────────────────────────────────────────
# Spike simulation — triggers an alert every ~30 readings
# ─────────────────────────────────────────
SPIKE_PROBABILITY = 0.05   # 5% chance per reading

def generate_pressure(step: int) -> float:
    """
    Simulates realistic pressure oscillation using a sine wave
    centered in the normal range, with optional random spike.
    """
    if random.random() < SPIKE_PROBABILITY:
        # Spike: go above max threshold
        return round(random.uniform(168.0, 175.0), 2)

    # Normal sine-wave oscillation between 143 and 162 bar
    base   = (PRESSURE_NORMAL_MIN + PRESSURE_NORMAL_MAX) / 2   # 152.5
    amp    = 9.5
    value  = base + amp * math.sin(step * 0.15)
    noise  = random.uniform(-1.5, 1.5)
    return round(value + noise, 2)


def generate_temperature(step: int) -> float:
    """
    Simulates realistic temperature rise during the day,
    with occasional spike above the threshold.
    """
    if random.random() < SPIKE_PROBABILITY:
        # Spike: go above max threshold
        return round(random.uniform(47.0, 55.0), 2)

    # Slow rising trend over time, noisy
    base  = (TEMP_NORMAL_MIN + TEMP_NORMAL_MAX) / 2   # 31.5
    drift = 6.5 * math.sin(step * 0.05)
    noise = random.uniform(-2.0, 2.0)
    return round(base + drift + noise, 2)


def build_payload(metric: str, value: float, unit: str) -> str:
    """Returns a JSON string ready to publish on MQTT."""
    return json.dumps({
        "sphere_id":  SPHERE_ID,
        "metric":     metric,
        "value":      value,
        "unit":       unit,
        "timestamp":  datetime.datetime.utcnow().isoformat() + "Z"
    })


# ─────────────────────────────────────────
# MQTT connection callbacks
# ─────────────────────────────────────────
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[✓] Connecté au broker MQTT ({BROKER_HOST}:{BROKER_PORT})")
        print(f"[→] Publication sur le topic : {TOPIC}")
        print(f"[~] Intervalle : {INTERVAL}s\n")
    else:
        print(f"[✗] Échec de connexion — code retour : {rc}")


def on_publish(client, userdata, mid):
    pass  # Silent — we log ourselves below


# ─────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────
def main():
    client = mqtt.Client(client_id="gpl_simulator")
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"[…] Connexion au broker MQTT {BROKER_HOST}:{BROKER_PORT} …")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    step = 0
    try:
        while True:
            pressure    = generate_pressure(step)
            temperature = generate_temperature(step)

            # Publish pressure
            payload_p = build_payload("pressure", pressure, "bar")
            client.publish(TOPIC, payload_p, qos=1)

            # Publish temperature (slight delay so they're separate messages)
            time.sleep(0.1)
            payload_t = build_payload("temperature", temperature, "°C")
            client.publish(TOPIC, payload_t, qos=1)

            # Console log with alert indicator
            p_alert = "🔴 ALERTE" if pressure  > PRESSURE_NORMAL_MAX or pressure  < PRESSURE_NORMAL_MIN else "🟢 OK"
            t_alert = "🔴 ALERTE" if temperature > TEMP_NORMAL_MAX    or temperature < TEMP_NORMAL_MIN    else "🟢 OK"

            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}]  "
                  f"Pression: {pressure:>7.2f} bar  {p_alert}   |   "
                  f"Température: {temperature:>6.2f} °C  {t_alert}")

            step += 1
            time.sleep(INTERVAL - 0.1)

    except KeyboardInterrupt:
        print("\n[■] Simulateur arrêté.")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
