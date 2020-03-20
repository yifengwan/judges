# Chinese judges 中国法官目录


+ data source: [China Judicial Process Information Online (中国审判流程公开网)](https://splcgk.court.gov.cn/gzfwww/).
+ codes: `list.py`  , a web scraper. 3486 courts in total on the source website.
+ data: in csv/json format.
    + `courts.csv/json`, collection of courts, comparable to the collection [here](https://github.com/yifengwan/court-system). The latter collection has more detailed information and classification.
    + `judges.csv/json`, collection of judges, their name, sex, department (in a court), administrative rank, court name, province. 69666 judges in total with information.
    + `courts_nodata.csv/json`, list of courts that do not have information about their judges on the website. 1061 courts.
