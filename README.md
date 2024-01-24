# Bootleg-Youtube-Premium 

<a href="https://youtu.be/hxSG5vPsVnA" target="_blank"><img src="https://img.youtube.com/vi/hxSG5vPsVnA/0.jpg" 
alt="img" width="240" height="180" border="10" /></a>

https://youtu.be/hxSG5vPsVnA

I don't like paying $15 a month to listen to youtube videos with my phone locked. 
`Bootleg-Youtube-Premium` integrates iOS shortcuts, a remote apache server and the python
youtube-dl library to give you "most" of the youtube premium features at a fraction of the
price.

## Server-Side installation 

```bash 
sudo apt install apache2 yt-dlp
systemctl start apache2
systemctl enable apache2
ufw allow 80
ufw allow 443
git clone https://github.com/NotJoeMartinez/bootleg-youtube-premium
cd bootleg-youtube-premium 
chmod +x dl_script.py sync.sh
pip3 install -r requirements.txt
sudo mkdir /var/www/html/videos
```

## iOS installation 

You'll need to use the [shortcuts](https://apps.apple.com/us/app/shortcuts/id915249334) app for this. It has a feature that allows you
to run scripts over ssh.      

![im1](imgs/img1.jpg)
