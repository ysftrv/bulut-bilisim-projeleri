import time
import boto3
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ---- AYARLAR ----
REGION = "us-east-1"
TABLO = "akilli-sehir-veriler"
CIHAZ = "akilli-sehir-sensor2"
SON_N = 30   # ekranda gosterilecek son olcum sayisi

dynamodb = boto3.resource("dynamodb", region_name=REGION)
tablo = dynamodb.Table(TABLO)

fig, ax = plt.subplots(figsize=(10, 5))

def veri_cek():
    resp = tablo.scan()
    items = [i for i in resp.get("Items", []) if i.get("cihaz_id") == CIHAZ]
    items.sort(key=lambda x: int(x["zaman"]))
    return items[-SON_N:]

def guncelle(frame):
    items = veri_cek()
    if not items:
        return
    zamanlar = [time.strftime("%H:%M:%S", time.localtime(int(i["zaman"]))) for i in items]
    sicaklik = [float(i["sicaklik"]) for i in items]
    hava     = [float(i["hava_kalitesi"]) for i in items]

    ax.clear()
    ax.plot(zamanlar, sicaklik, marker="o", label="Sicaklik (C)")
    ax.plot(zamanlar, hava, marker="s", label="Hava Kalitesi (AQI)")
    ax.set_title("Akilli Sehir Sensoru - Canli Veri (DynamoDB'den)")
    ax.set_xlabel("Zaman")
    ax.set_ylabel("Deger")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

# her 2 saniyede bir grafigi yenile
ani = animation.FuncAnimation(fig, guncelle, interval=2000)
plt.show()