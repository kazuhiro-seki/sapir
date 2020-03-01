# S-APIR: turning news texts into business sentiment

## Preface

This is a repository of the demonstration system of my ongoing work, partly carried out as an [APIR](https://www.apir.or.jp) research project, to turn news articles into business sentiment. The system also let you analyze any given factors that may/may not influence business sentiment. More features are planned to be added. Stay tuned!

## Requirements

Softwares
 * Python3
 * Elasticsearch and Kuromoji (for Japanese tokenization)
 * SQLite

Python libraries
 * elasticsearch
 * Flask
 * Flask-SQLAlchemy
 * SQLAlchemy

The codes were tested on MacOS.

## Instruction to run the codes

0. Install all the required softwares and libraries

1. Clone the repository
```sh
git clone https://github.com/kazuhiro-seki/sapir.git
```

2. Run indexer
```sh
python index.py --input data.txt  
```
Note that data.txt is not included in this repository due to the copyright.

3. Run the system
```sh
export FLASK_ENV=development; env FLASK_APP=sapir.py flask run
```

## Grants

This work was partially supported by JSPS KAKENHI grant #JP18K11558 and MEXT, Japan. 
