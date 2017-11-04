# Deal with Tor (save yourself from ip Blocking from you ISP)
First of all, lets install Tor.
- `apt-get update`
- `apt-get install tor`
- `/etc/init.d/tor restart`

You will notice that socks listener is on port 9050.

### You have to create a hashed password out of your password using:

- `tor --hash-password mypassword`

So, update the torrc with the port and the hashed password. open following file.

- `/etc/tor/torrc`

enable following lines

- `ControlPort 9051`
- `HashedControlPassword <your hash password>`

Restart Tor again to the configuration changes are applied.

- `/etc/init.d/tor restart`

## install PyTorCtl in your Python environment

Install pytorctl which is a python based module to interact with the Tor Controller.

- `apt-get install git`
- `apt-get install python-dev python-pip`
- `git clone git://github.com/aaronsw/pytorctl.git`
- `pip install pytorctl/`


## Privoxy (make Tor workable using proxy)
Tor itself is not a http proxy. So in order to get access to the Tor Network, we will use the Privoxy as an http-proxy though socks5..

Install Privoxy.

- `apt-get install privoxy`

Now lets tell privoxy to use TOR. This will tell Privoxy to route all traffic through the SOCKS servers at localhost port 9050.
Go to 

- `/etc/privoxy/config` 

and enable forward-socks5:

- `forward-socks5 / localhost:9050 .`
- `Restart Privoxy after making the change to the configuration file.`


restart privoxy

- `/etc/init.d/privoxy restart`



## install dependecies of crawler

- goto the `/scrapper` directory

install all dependencies from requirements.txt

- pip install -r requirements.txt

### run crawlwr
(run with sudo for resolve permission issue of torctrl)

- `sudo python scripts/<file-name>.py`

Data will be saved as `.csv` inside the `data/` directory.

happy coding :smile:
