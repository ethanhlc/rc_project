import cv2

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()     # init QRcode Detector

while True:
    ret, img = cap.read()

    data, bbox, qr_img = detector.detectAndDecode(img)

    if len(data) > 0:   # qr detected
        cv2.putText(img, data, (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
        # cv2.imshow('qr', qr_img)    # displa qr
        print(data)

    cv2.imshow('image', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
