import json
import time
import random
import os
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# ---- AYARLAR (senin bilgilerinle dolduruldu) ----
KLASOR = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "a3kkfuy295ynxd-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "akilli-sehir-sensor2"
TOPIC = "akilli-sehir/sensor"

CERT = os.path.join(KLASOR, "ee535723b622fffd5bbacdfed6d9c6c6a3474b28954c5226e3c3ffbc6f06314f-certificate.pem.crt")
KEY  = os.path.join(KLASOR, "ee535723b622fffd5bbacdfed6d9c6c6a3474b28954c5226e3c3ffbc6f06314f-private.pem.key")
CA   = os.path.join(KLASOR, "AmazonRootCA1.pem")

# AWS IoT Core'a guvenli baglanti kur
print("AWS IoT Core'a baglaniliyor...")
mqtt_connection = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=CERT,
    pri_key_filepath=KEY,
    ca_filepath=CA,
    client_id=CLIENT_ID,
    clean_session=False,
    keep_alive_secs=30,
)
mqtt_connection.connect().result()
print("Baglandi! Veri gonderiliyor (durdurmak icin Ctrl+C)...\n")

# Sahte akilli sehir sensoru: her 2 saniyede bir veri uret ve gonder
try:
    while True:
        veri = {
            "cihaz_id": CLIENT_ID,
            "zaman": int(time.time()),
            "sicaklik": round(random.uniform(18, 35), 1),   # derece C
            "nem": round(random.uniform(30, 80), 1),         # yuzde
            "hava_kalitesi": random.randint(20, 150),        # AQI
        }
        mqtt_connection.publish(
            topic=TOPIC,
            payload=json.dumps(veri),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        print("Gonderildi:", veri)
        time.sleep(2)
except KeyboardInterrupt:
    print("\nDurduruluyor...")
    mqtt_connection.disconnect().result()
    print("Baglanti kapatildi.")