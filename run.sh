conda activate ghlisten
cd /home/mcfrank/celium/ghlisten

export PATH_CELIUM="/home/mcfrank/celium"
export REPO="m-c-frank/posts"
export PATH_INPUT="/home/mcfrank/posts"
export PATH_DB="data/issues.db"

mkdir -p data

python main.py