# Home Assistant P2PCam
Home Assistant custom integration to retrieve images from cameras using the p2pCamViewer app.

First of all, the original connection and retrieval process has been made by [Jheyman](https://github.com/jheyman/) in his [videosurveillance script](https://github.com/jheyman/videosurveillance/).
I rewrote it to run as a class instead of an application and added the Home Assistant code to it.

So I had this [chinese camera](https://usb.brando.com/ontop-p2p-rt8633-hd-high-density-night-vision-wireless-ipcam_p03365c43d15.html) laying around, it had this feature that you could access it from outside your home without the need for port forwarding. However after a couple of years this brand dissappeared and with it their services so I couldn't connect to it outside of my own network using [this app](https://plug-play.en.aptoide.com/app) which made owning this camera quite useless. But I had since gotten into Home Asssistant and got the idea to get it working in there since my instance ran locally so it should be able to access the camera.

## Installation

```bash
# Move to your Home Assistant configuration folder
cd <your-config-dir>

# Create the folder for this custom integration
mkdir -p custom_components/p2pcam && cd custom_components/p2pcam

# Download the required files
wget https://raw.githubusercontent.com/devmlb/home-assistant-p2pcam/refs/heads/master/camera.py
wget https://raw.githubusercontent.com/devmlb/home-assistant-p2pcam/refs/heads/master/utils.py
wget https://raw.githubusercontent.com/devmlb/home-assistant-p2pcam/refs/heads/master/manifest.json

# Edit your HA configuration file
cd ../.. && nano configuration.yaml
```

Add these lines:
```
camera:
  - platform: p2pcam
    name: <camera name>
    host: <IP address of the machine running Home Assistant>
    ip_address: <IP address of your camera>
```
e.g.
```
camera:
  - platform: p2pcam
    name: ontop
    host: 192.168.178.5
    ip_address: 192.168.178.9
```

Press `Ctrl + O`, `Enter` and `Ctrl + X`.  
Then restart Home Assistant.

> The connection method of these cameras seem quite dodgy so it may take a little while sometimes for the image to be fetched.  
> This will no longer be a problem once a connection has been established and the stream is being received.

## Disclaimer

I am not an experienced Python or Home Assistant component developer. This is one of my first projects for this, so I would love feedback and [Pull requests](https://github.com/indykoning/home-assistant-p2pcam/pulls) to improve this and maybe even get it into the core.