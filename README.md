# somnilopy
### A sound-activated sleep talking recorder

### About
A sleeptalking recorder for high quality audio. It polls for sleeptalking within a schedule and serves a simple, static HTML and JavaScript front-end that allows you to download, stream, delete, and categorise sleeptalking files.

### Run on Linux
Frontend:
Install requirements with:
```
sudo apt-get install npm
sudo npm install http-server -g
```
Run the somnilopy frontend by cloning the repo and running, from the frontend working directory
```
working_dir/frontend $ npm http-server
```


Backend: 
First, clone the repo and install any missing requirements, including sphixbase and its dependencies:
```
git clone https://github.com/mfmmq/somnilopy.git
sudo apt-get install sphinxbase gcc automake autoconf libtool bison swig python-dev libpulse-dev  
pip install -r requirements.txt
```
Run the somnilopy backend with
```
working_dir $ python run.py --help
```

### Requirements
pyaudio, npm, sphinxbase

