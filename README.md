# S-APIR: turning news texts into business sentiment

## About

This is a repository of the demonstration system of my ongoing work, partly carried out as an [APIR](https://www.apir.or.jp) research project, "development and application of new business sentiment index based on textual data". The system also let you analyze any given factors that may/may not influence business sentiment. More features are planned to be added. Stay tuned!

## Requirements

Software
 * Python3
 * Elasticsearch 6.X and Kuromoji (for Japanese tokenization)
 * SQLite

Python libraries
 * elasticsearch
 * Flask
 * Flask-SQLAlchemy
 * SQLAlchemy

The codes were tested on MacOS.

## Instructions on how to run the codes

0. Install all the required software and libraries

1. Clone the repository
```sh
git clone https://github.com/kazuhiro-seki/sapir.git
```

2. Run indexer (Note that data.txt is not included in this repository due to the copyright.)
```sh
python index.py --input data.txt  
```


3. Run the system
```sh
export FLASK_ENV=development; env FLASK_APP=sapir.py flask run
```

4. Open [http://127.0.0.1:5000/sapir](http://127.0.0.1:5000/sapir) in your browser

<img src="/figs/demo.png" width="600">

## Grants

This work was partially supported by JSPS KAKENHI grant #JP18K11558 and MEXT, Japan. 

## Reference

* Kazuhiro Seki and Yusuke Ikuta. Estimating Business Sentiment from News Texts. In *Proceedings of the 2nd IEEE Artificial Intelligence and Knowledge Engineering*, pp. 55-56, 2019.

* Kazuhiro Seki and Yusuke Ikuta. S-APIR: News-based Business Sentiment Index. arXiv:2003.02973 [cs.CL], 2020. [https://arxiv.org/abs/2003.02973](https://arxiv.org/abs/2003.02973)
