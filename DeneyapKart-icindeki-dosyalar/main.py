####
# upip.install("picoweb")
# upip.install("micropython-ulogging")

# adapted from https://github.com/lemariva/uPyCam/blob/master/webcam.py
import deneyap
from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import utime

import framebuf
import images_repo2

# using default address 0x3C
i2c = SoftI2C(sda=Pin(4), scl=Pin(15))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

import machine

import network
import utime
import ntptime

import camera
import picoweb
import time
import uasyncio as asyncio


##### wifi connection
ssid = 'SUPERONLINE_MNK_OGR'
password = 'R2zCtEZzaz'

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    start = utime.time()
    timed_out = False

    if not sta_if.isconnected():
        print('Aga baglaniliyor...')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected() and \
            not timed_out:        
            if utime.time() - start >= 20:
                timed_out = True
            else:
                pass

    if sta_if.isconnected():
        ntptime.settime()
        print('Baglanti saglandi: ', sta_if.ifconfig())
    else: 
        print('Baglanti yok!')


##### web app
app = picoweb.WebApp('app')

@app.route('/stream')
def index(req, resp):
    stream = True # single frame or stream
    
    if (not camera.init(0,
            d0=19, d1=22, d2=23, d3=21, d4=18, d5=26, d6=35, d7=34,
            href=39, vsync=36, reset=-1, sioc=25, siod=33, xclk=32, pclk=5, pwdn=-1,
            format=camera.JPEG, framesize=camera.FRAME_VGA, 
            xclk_freq=camera.XCLK_10MHz,fb_location=camera.PSRAM)):
        camera.deinit()
        await asyncio.sleep(1)
        # If we fail to init, return a 503
        if (not camera.init(0,
            d0=19, d1=22, d2=23, d3=21, d4=18, d5=26, d6=35, d7=34,
            href=39, vsync=36, reset=-1, sioc=25, siod=33, xclk=32, pclk=5, pwdn=-1,
            format=camera.JPEG, framesize=camera.FRAME_VGA, 
            xclk_freq=camera.XCLK_10MHz,fb_location=camera.PSRAM)):
                yield from picoweb.start_response(resp, status=503)
                yield from resp.awrite('HATA: Kamera baslatilamadi!\r\n\r\n')
                return
            
    # wait for sensor to start and focus before capturing image
    await asyncio.sleep(2)
    
    n_frame = 0
    while True:
        n_try = 0
        buf = False
        while (n_try < 10 and buf == False): #{
            # wait for sensor to start and focus before capturing image
            buf = camera.capture()
            if (buf == False): await asyncio.sleep(2)
            n_try = n_try + 1
    
        if (not stream):
            camera.deinit()    

        if (type(buf) is bytes and len(buf) > 0):
            try:
                if (not stream):
                    yield from picoweb.start_response(resp, "image/jpeg")
                    yield from resp.awrite(buf)
                    print('JPEG: Frame gonderildi')
                    break
            
                if (n_frame == 0): 
                    yield from picoweb.start_response(resp, "multipart/x-mixed-replace; boundary=myboundary")
            
                yield from resp.awrite('--myboundary\r\n')
                yield from resp.awrite('Content-Type:   image/jpeg\r\n')
                yield from resp.awrite('Content-length: ' + str(len(buf)) + '\r\n\r\n')
                yield from resp.awrite(buf)

            except:
                # Connection gone?
                print('Baglanti sonlandi!')
                camera.deinit()
                return

        else: 
            if (stream):
                camera.deinit()
        
            #picoweb.http_error(resp, 503)
            yield from picoweb.start_response(resp, status=503)
            if (stream and n_frame > 0): 
                yield from resp.awrite('Content-Type:   text/html; charset=utf-8\r\n\r\n')
            
            yield from resp.awrite('Hata:\r\n\r\n' + str(buf))
            return
        
        print('MJPEG: Gonderilen frame ' + str(n_frame))
        n_frame = n_frame + 1
        
"""
@app.route("/receive_data")
def receive_data(req, resp):
    # Get the data from the request body
    data = yield from req.read_form_data()
        
    # Do something with the data
    print("Received data:", data)
    
    # Send a response back to the client
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Data received")
"""    

@app.route("/receive_data")
def receive_data(req, resp):
    if req.method == "POST":
        yield from req.read_form_data()
    else:  # GET, apparently
        # Note: parse_qs() is not a coroutine, but a normal function.
        # But you can call it using yield from too.
        req.parse_qs()

    # Whether form data comes from GET or POST request, once parsed,
    # it's available as req.form dictionary

    yield from picoweb.start_response(resp)
    yield from resp.awrite("Emotion: %s!" % req.form["name"])
    print(req.form["name"])
    
    if not req.form["name"]:
        pass
        
    else:
        if req.form["name"] == 'Angry':
            buffer = images_repo2.duygu_list[0]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Disgust':
            buffer = images_repo2.duygu_list[1]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Fear':
            buffer = images_repo2.duygu_list[2]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Happy':
            buffer = images_repo2.duygu_list[3]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Neutral':
            buffer = images_repo2.duygu_list[4]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Sad':
            buffer = images_repo2.duygu_list[5]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
        elif req.form["name"] == 'Surprise':
            buffer = images_repo2.duygu_list[6]

            fb = framebuf.FrameBuffer(buffer, 128, 64, framebuf.MONO_HLSB)
            display.fill(0)
            display.blit(fb, 8, 0)

            display.show()
            utime.sleep_ms(200)
            
    

def run():
    app.run(host='0.0.0.0', port=80, debug=True)


##### start
do_connect()
run()

