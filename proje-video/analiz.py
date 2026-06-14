import boto3
import time

# ---- AYARLAR ----
BUCKET = "bulut-dersi-video-yusuf"   # senin kova adın
VIDEO = "test-video.mp4"             # S3'e yüklediğin video adı
REGION = "us-east-1"

# Rekognition'a bağlan
rekognition = boto3.client("rekognition", region_name=REGION)

print("Video analizi baslatiliyor...")

# 1) Analiz isini baslat (AWS'de asenkron calisir)
start = rekognition.start_label_detection(
    Video={"S3Object": {"Bucket": BUCKET, "Name": VIDEO}},
    MinConfidence=70   # sadece %70 ustu guvendeki etiketleri al
)
job_id = start["JobId"]
print("Is ID:", job_id)

# 2) Is bitene kadar bekle
print("Analiz suruyor, lutfen bekleyin...")
while True:
    result = rekognition.get_label_detection(JobId=job_id)
    status = result["JobStatus"]
    if status in ("SUCCEEDED", "FAILED"):
        break
    time.sleep(5)   # 5 saniyede bir kontrol et

if status == "FAILED":
    print("Analiz basarisiz oldu.")
    exit()

# 3) Tum sonuc sayfalarini topla
labels = result["Labels"]
next_token = result.get("NextToken")
while next_token:
    result = rekognition.get_label_detection(JobId=job_id, NextToken=next_token)
    labels.extend(result["Labels"])
    next_token = result.get("NextToken")

# 4) Etiketleri benzersiz hale getir (en yuksek guven puaniyla)
bulunanlar = {}
for item in labels:
    ad = item["Label"]["Name"]
    guven = item["Label"]["Confidence"]
    if ad not in bulunanlar or guven > bulunanlar[ad]:
        bulunanlar[ad] = guven

# 5) Sonuclari ekrana yazdir
print("\n=== VIDEODA TANINAN NESNELER/ETIKETLER ===\n")
for ad, guven in sorted(bulunanlar.items(), key=lambda x: x[1], reverse=True):
    print(f"  - {ad}: %{guven:.1f}")

print(f"\nToplam {len(bulunanlar)} farkli etiket bulundu.")