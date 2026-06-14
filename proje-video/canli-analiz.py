import boto3
import cv2

# ---- AYARLAR ----
VIDEO = "test-video.mp4"   # bilgisayarindaki video (proje-video klasorunde olmali)
REGION = "us-east-1"
KARE_ARALIGI = 60          # her 30 karede bir AWS'ye sor (ucretsiz sinirda kalmak icin)

rekognition = boto3.client("rekognition", region_name=REGION)

cap = cv2.VideoCapture(VIDEO)
if not cap.isOpened():
    print("Video acilamadi. Dosya adini ve klasoru kontrol et.")
    exit()

print("Canli analiz basliyor. Cikmak icin pencereyi secip 'q' tusuna bas.")

kare_no = 0
son_etiketler = []

while True:
    ret, frame = cap.read()
    if not ret:
        break   # video bitti
    kare_no += 1

    # Belirli araliklarla bir kareyi AWS'ye gonder
    if kare_no % KARE_ARALIGI == 0:
        ok, encoded = cv2.imencode(".jpg", frame)
        if ok:
            cevap = rekognition.detect_labels(
                Image={"Bytes": encoded.tobytes()},
                MaxLabels=5,
                MinConfidence=80
            )
            son_etiketler = [
                f"{l['Name']} %{l['Confidence']:.0f}"
                for l in cevap["Labels"]
            ]

    # O anki etiketleri karenin uzerine yaz
    y = 30
    for etiket in son_etiketler:
        cv2.putText(frame, etiket, (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        y += 35

    cv2.imshow("Canli Video Analizi (AWS Rekognition)", frame)

    # 'q' tusuna basinca cik
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("Analiz tamamlandi.")