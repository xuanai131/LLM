import time
import threading

def scan_barcode(barcode_ready_event):
    t = time.time()
    while True:
        print("scanning")
        end_time = time.time()
        if end_time - t > 20:
            barcode_ready_event.set()
            return "overtime"

def get_input(barcode_ready_event):
    barcode_ready_event.wait()  # Wait until barcode scanning is complete
    user_input = input("Enter input: ")
    return user_input

def synchronized_scan_and_input():
    barcode_ready_event = threading.Event()
    barcode_thread = threading.Thread(target=scan_barcode, args=(barcode_ready_event,))
    input_thread = threading.Thread(target=get_input, args=(barcode_ready_event,))
    
    barcode_thread.start()
    input_thread.start()
    
    barcode_thread.join()
    input_thread.join()

synchronized_scan_and_input()
