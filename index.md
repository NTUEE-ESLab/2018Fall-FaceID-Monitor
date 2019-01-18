# Face-ID Monitor

## Features
- Face Detection
- Motion Detection
- Mail alarm
- Python module with tunable parameters

## Scenario
The camera keeps detecting motion. When motion is detected, the authorized face must be detected within a buffer time to release the alarm; otherwise, the buzzer will ring, and Pi will send images by e-mail.

## Requirements
SMTP function must be installed, which is not contained in python functions. Refer to the reference below to setup the SMTP server.
Other modules that are required are:
- `click==6.7`
- `Flask==0.12.2`
- `itsdangerous==0.24`
- `Jinja2==2.9.6`
- `MarkupSafe==1.0`
- `picamera==1.13`
- `Werkzeug==0.12.2`
- `numpy==1.13.1`
- `opencv-python==4.0.0`


## Software Structure
### Main thread
<img src="https://i.imgur.com/PgR5Ydy.png" width="180">

### Camera thread
<img src="https://i.imgur.com/cQfrl1c.png" width="350">

### Motion detection module
<img src="https://i.imgur.com/o67uo9Y.png" width="350">

### Face detection module
<img src="https://i.imgur.com/poDXdj2.png" width="350">

### Indicators thread
<img src="https://i.imgur.com/PbzsXFQ.png" width="300">

### Mail script
<img src="https://i.imgur.com/WHh6YdX.png" width="300">


## How to use

### Face registeration
First, you have to register your face into the machine. By uploading your photos (recommended less than 2K in both width and length) into the `dataset/` directory. You should create a new folder named as your name and put your photos into the folder. e.g.
- `dataset/Mike/IMG_0001.JPG`
- `dataset/Mike/IMG_0002.JPG`
- `dataset/Mike/IMG_0003.JPG`
- `dataset/Kevin/IMG_0045.JPG`
- `dataset/Kevin/IMG_0049.JPG`
- `dataset/Kevin/IMG_0148.JPG`

After that, execute `python3 encode_faces.py` to encode faces into a single file. Then this file will be used by the following face detection module

### Setup your mail address and message
In `mail.txt`, you can set your own mail. Note that `FROM/TO/Subject` rows must be included; otherwise the mail may fail to be sent out.

### run the main thread
Last, execute `python3 app.py` to run all the functions including **http streaming**, **motion detection**, **face detection**, **LED and buzzer alarm**, and **mail alarm**

## Tunable parameters
- In `camera_opencv.py`,
    - `ALARM_BUFFER`: buffer time after motion is detected. This value can be set larger if false alarm is too frequent
    - `AUTH_BUFFER`: buffer time after face detection to prevent frequent face detection which may sometimes be annoying. Set this value lower if miss happens.
    - `ALARM_DURATION`: max time that alarm will last.

- In `mail.txt`,
    - `FROM:` the sender name that will be presented by the mail receiver
    - `TO:` the receiver mail address
    - `BCC:` BCC address if needed
    - `Reply-To:` the reply-to address for this mail
    - `Subject:` the subject of this mail

- In `dataset/`, create your own folders with your name as folder name, containing photos of yours

## SWOT analysis
### Strength
- Low power
- Light-weighted
- Wireless LAN supported
- Integration from capturing to alarming and selective recording
- Highly modularized funciton
- Tunable paremeters

### Weakness
- Low resolution (480p) and frame rate (6fps) due to limited computing capability
- WLAN does not support enterprise security
- Haar detection is not rotation-resistant, causing low precision on face detection
- RPi has 4 threads of CPU, but few programs can fully utilize them. Despite, the clock rate of a single core is rather low.
- The model applies HOG for face recognition, which cannot beat the state-of-art method CNN. But CNN cannot be applied on RPi due to computing complexity

### Opportunities
- Let the RPi concentrate at recording and streaming, put computing-intensive job at remote server

### Threats
- Monitors with 1080p30 are everywhere on the market with rather low price.

## Demo video
[https://youtu.be/v7BJr0ogYmM](https://youtu.be/v7BJr0ogYmM)

## References
- [Flask](https://github.com/miguelgrinberg/flask-video-streaming )
- [SMTP server](https://www.hackster.io/gulyasal/make-a-mail-server-out-of-your-rpi3-5829f0)
- [Pi Face Recognition](https://www.pyimagesearch.com/2018/06/25/raspberry-pi-face-recognition/) 
- [Pi Motion Detection](https://blog.gtwang.org/programming/opencv-motion-detection-and-tracking-tutorial/)
- [Python Docs](https://docs.python.org/3/)
- [OpenCV Docs](https://docs.opencv.org/4.0.1/)
