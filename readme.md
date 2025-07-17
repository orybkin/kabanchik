# A bot scraping freelance tasks from kabanchik.ua

A simple bot using selenium in python that logs into an account, checks tasks, and sends a telegram message when there is a new task.

# Usage
```
cd ~/code/kabanchik/
conda activate /home/oleh/code/kabanchik/.conda/envs/kabanchik
python kabanchik.py
```

# OR 
```
git clone https://github.com/orybkin/kabanchik.git
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
source ~/miniconda3/bin/activate
conda create -n kabanchik python=3.11
source activate 
cd kabanchik
pip install selenium bs4
```
or something like that idk
