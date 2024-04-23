import cv2
import time
from pyzbar.pyzbar import decode
def scan_barcode(ten_sach: str):  # define scan function to scan barcode
    t = time.time()
    # image_path = '384543478_1440448783351821_8320517275639987477_n.jpg'  # Replace 'images' with the path to your directory
    # image = cv2.imread(image_path)
    print('captured1')
    cap = cv2.VideoCapture(0)
    print('captured2')
    if not cap.isOpened():
        print('captured3')
        return "Không có camera để quét barcode"
    print('captured4')
    while True:
        # Capture frame-by-frame
        ret, image = cap.read()
        # print('captured5')
        # cv2.imshow('image', image)
        print('captured6')
        if cv2.waitKey(1) == ord('q'):
            cap.release()
            # cv2.destroyAllWindows()
            # cv2.destroyWindow('image')
            # break
        
        if (time.time() - t) > 20:
            return "OVERTIME"
        try:
            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect barcodes in the image
            decoded_objects = decode(gray)


            # Process each detected barcode and cut it into a new image
            for i, obj in enumerate(decoded_objects):
                data = obj.data.decode('utf-8')  # Extract the barcode data
                cap.release()
                # cv2.destroyAllWindows()
                # cv2.destroyWindow('image')
                return data
        except:
            continue
answer = scan_barcode("f")
print(answer)