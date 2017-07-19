# RSS-feeds auto downloader

## Features:
* Download specified torrents in RSS-feeds to specifed path at indicated intervals
* Key-words filter: Download torrents of interest from the RSS-feeds filted by key-words
* E-mail notification: As an option, an e-mail can be sent each time the download has been finished

## Useage:
Start/Stop the process in daemon mode:
```bash
python ./td.py -c xxx.json -d start
python ./td.py -c xxx.json -d stop
```
The xxx.json mentioned above is a config file, the example format of which can be found in example.json. The arguments '-d start' means start process in daemon mode.

## Config file:
**time** The interval identified to download  
**tdir** The directory to save torrents  
**tdirs** The directories to determine the exsistance of a torrent  
**ctrl-dir** The directory for database and log file(s)  
**rss** The list for RSS-feeds  
**address** The address of RSS-feed  
**parser** The parser for RSS-feed analysis. Support analysis for TTG, HDC, HDRout, OpenCD(input in lower case). Other than the parers mentioned above, the 'default' parser might be an option  
**subscriber/subscribers** The E-mail address(es) for subscriber(s).
**filter** Filter-rule list, multiple filter-rules can be set, the relationship among them is 'or'.  
**key-words** Key-word list, multiple key-words can be set, the relationship among them is 'and'.  
**key-regex** Key-word-regular-expression list, for download all episodes in the certain season(eg. S01Exx), regular-expression can be chosen.  

## About filter-rule
Once a torrent matched has been downloaded, it will not be downloaded again if matched again.  

For example, the filter-rules as follows:
```javascript
{
    "key-words": ["Game of Thrones", "CtrlHD"],
    "key-regex": []
}
```
If there are two new torrents with names:  
> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E10 1080i HDTV MPEG2 DD5 1-CtrlHD  

Although both of them match the filter-rules, only S06E09 will be downloaded, In case of downloaded the same episode from different sources or with different resolutions repeatly, eg.  

> Game of Thrones S06E09 720p HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   

To solve the problem, add a filter-rule to key-regex as followed:
```javascript
{
    "key-words": ["Game of Thrones", "CtrlHD"],
    "key-regex": ["S06E\\d+"]
}
```
Accoding to the filter-rules above, in the three new following torrents, only the first S06E09 and S06E10 will be downloaded, but not the second S06E09.  

> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E09 720p HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E10 1080i HDTV MPEG2 DD5 1-CtrlHD  


