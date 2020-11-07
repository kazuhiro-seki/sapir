# S-APIR: Turning news texts into business sentiment

## About

This is a repository of the [demonstration system](http://44.237.209.189/sapir) of my ongoing work, partly carried out as an [APIR](https://www.apir.or.jp) research project, "development and application of new business sentiment index based on textual data". The system also let you analyze any given factors that may/may not influence business sentiment. More features are planned to be added. Stay tuned!

## Requirements

Software
 * Python 3
 * Elasticsearch 6.X and Kuromoji (for Japanese tokenization)
 * SQLite

Python libraries
 * elasticsearch
 * Flask
 * Flask-SQLAlchemy
 * SQLAlchemy

The codes were tested on macOS Catalina and CentOS 7.

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

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. An example query "増税" (tax increase) is preset in the text box for convenience.

<img src="/figs/landing.png" width="600">

5. Search the example query or any other keywords to find out thier influences on business sentiment. For the example of "増税", we can see from the resulting plot that there have been multiple periods in which tax increase had notable negative effects and the one in 2014 had the biggest impact. The query specific data can be downloaded as a csv file by clicking the "csv" button.

<img src="/figs/tax.png" width="600">

## Demo system

You can play with the demo system at [http://44.237.209.189/sapir](http://44.237.209.189/sapir). Note that it currently accepts only Japanese queries. If the demo system doen't work for some reason, try deleting its cache by clicking [here](http://44.237.209.189/sapir/delete).

## Acknowledgments

This work was partially supported by JSPS KAKENHI \#JP18K11558 and MEXT, Japan. We
thank Hideo Miyahara, Hiroshi Iwano, Yuzo Honda, Yoshihisa Inada,
Yoichi Matsubayashi, and Yusuke Ikuta for their support.  The Nikkei
data were provided by APIR.

## Reference

Kazuhiro Seki and Yusuke Ikuta. S-APIR: News-based Business Sentiment Index. In Proceedings of the 24th European Conference on Advances in Databases and Information Systems, pp. 189-198, August 2020.
