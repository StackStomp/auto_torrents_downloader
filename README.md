# RSS-feeds 自动下载器

## 特性:
* 定时下载指定RSS-feeds中的种子，到指定目录
* 关键词过滤，通过关键词过滤指定的RSS-feed，只下载感兴趣的种子
* 邮件通知，在每次下载种子之后，可选择邮件通知到指定的email邮箱，调用mail功能

## 使用方法:
以守护进程方式启动运行/结束运行：
```bash
python ./td.py -c xxx.json -d start
python ./td.py -c xxx.json -d stop
```
其中xxx.json为配置文件，格式可参考example.json，-d start为守护进程方式启动

## 配置文件：
**time**  
**tdir** 种子保存目录  
**tdirs** 种子读取目录（如果有多个种子保存目录，且希望其他目录也被统计)  
**ctrl-dir** 控制目录，用于存放数据库，log等  
**rss** RSS-feeds配置list，内存放RSS-feeds信息  
**address** RSS-feed地址
**parser** 使用哪个解析器解析此feed，目前支持的有TTG,HDC,HDRout,OpenCD(填入时使用小写字母)，另外有一种default方式，如果在这四种之外，可以尝试一下是否可行。
**subscriber/subscribers** 订阅者email，subscriber为字符串，若有多个订阅者，使用subscribers（list）
**filter** 过滤规则list，可以指定多组过滤规则，每组过滤器之间为或的关系。即满足其中任意一组，则下载该种子  
**key-words** 关键字list，可以指定多组关键字，关键字之间为与的关系。即必须关键字全部匹配，本过滤规则才算匹配  
**key-regex** 关键字正则表达式list，如果关键字list无法满足要求(例如要匹配第一季的所有剧集S01Exx)，则可以考虑使用正则表达式  

## 关于过滤规则
需要注意的是，一旦过滤规则匹配，下载了该种子，则再次匹配不会触发再次下载。  

例如过滤规则设置为
```javascript
{
    "key-words": ["Game of Thrones", "CtrlHD"],
    "key-regex": []
}
```
如果此时出现了两个新种子，文件名分别为：

> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E10 1080i HDTV MPEG2 DD5 1-CtrlHD  

由于S06E09已经匹配了规则，因此S06E10不再匹配。结果是只下载S06E09一个种子。这么做的原因是为了防止重复下载不同压制组或不同分辨率的同一个文件，例如：

> Game of Thrones S06E09 720p HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   

解决方法为，在key-regex中配置需要的剧集，如下：
```javascript
{
    "key-words": ["Game of Thrones", "CtrlHD"],
    "key-regex": ["S06E\\d+"]
}
```
以上配置，若出现如下三个文件，则工具下载S06E09和S06E10各一个，后出现的S06E09将不会下载：

> Game of Thrones S06E09 1080i HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E09 720p HDTV MPEG2 DD5 1-CtrlHD   
> Game of Thrones S06E10 1080i HDTV MPEG2 DD5 1-CtrlHD  

当然，如果想要指定下载1080i分辨率，可以在key-words中增加关键字1080i

## default_test.py的使用
default_test.py用于测试某RSS-feeds可否被default解析。  
例如RSS-feed地址为xxxx，测试方法为：
```bash
python default_test.py http://xxxx
```
查看打印的解析信息是否正确，若正确，则说明可以使用default解析  

### 使用前需要安装的包：
* feedparser
* bencode

