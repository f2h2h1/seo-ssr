针对 seo 的后端渲染
====================
这是一个针对 seo 的后端渲染，可以在不修改前端代码的情况下使 spa 的网站返回完整的渲染好的 html ，
仅针对搜索引擎的爬虫，普通用户访问时还是前端渲染

如果遇到什么问题，十分欢迎提 issues

## 依赖
- python 3.9
- playwright 1.8.0a1
- Chrome 80-90 之间的版本

## 安装
0. 安装 python ，并把 python 加入到环境变量
0. 安装 playwright ， `python -m pip install playwright==1.8.0a1`
0. 安装驱动用的浏览器，`python -m playwright install`
0. clone 项目
0. 复制 config-template.ini ，并重命名为 config.ini ，然后根据注释的提示修改配置

## 启动
使用默认的配置文件
`python server.py`

指定配置文件路径
`python server.py --config=config-user.ini`

启动后会在当前目录生成一个 playwright_temp 文件夹，是保存浏览器缓存用的

## docker
0. 打包镜像 `docker build -t myseo .`
0. 启动容器
```bash
docker run --restart always -d \
    --name seo \
    --ipc=host \
    -p 8081:8081 \
    -v `pwd`:/seo \
    -w  /seo \
    myseo python server.py
```

## 提示
- **部署到线上的时候，需要根据搜索引擎的爬虫来转发请求，一般是通过 ua 来判断的**
- 修改 hosts 文件，在内网访问网站能大幅提高速度
- 使用 docker 部署时要注意容器的 ip ，特别是容器访问宿主机时的 ip ，上面的 docker 启动命令仅供参考
- 这个方案不是很完美， python 自带的 http 服务并不能很好地应付大的并发，虽然大部分情况下针对爬虫不会有高的并发，首屏渲染的速度不能太慢，遇到懒加载的图片可能会加载不完整
- python 的 ThreadingMixIn 好像有内存泄漏（~~其实就是自己的代码没写好~~），最好弄个定时任务定时重启
- 可以在服务器里使用这样的命令测试是否生效，如果返回的是渲染好的 html ，则表示已经生效
```
curl "http://127.0.0.1:8081"
```
- 可以在服务器里使用这样的命令来测试页面的响应速度
```bash
curl -o /dev/null -s -w %{time_namelookup}::%{time_connect}::%{time_starttransfer}::%{time_total}::%{speed_download}"\n" "http://127.0.0.1:8081"
```

这是 nginx 大概的转发配置
```
    if ($http_user_agent ~* "(bing|yandex|yahoo|Yisou|baidu|360|sogou|APIs-Google|Mediapartners-Google|AdsBot-Google-Mobile|AdsBot-Google-Mobile|AdsBot-Google|Googlebot|Googlebot-Image|Googlebot-News|Googlebot-Video|Mediapartners-Google|AdsBot-Google-Mobile-Apps|FeedFetcher-Google|Google-Read-Aloud|DuplexWeb-Google|Google Favicon|googleweblight|Storebot-Google)"){
        proxy_pass http://127.0.0.1:8081;
    }
```

- 可以使用这样的命令测试 nginx 的转发是否生效，如果返回的是渲染好的 html ，则表示已经生效
```
curl -L --user-agent "bing" 网址
```

这是定时重启的 cron ，每天的 2 点重启，最好用 root 用户来执行
```
0 0 2 * * ? * docker restart seo
```

这个是作者部署在生产环境时的大致的架构图
```
                                                      普通用户的访问      +-------------++
                                                                         +              |
                                                   +-------------------> |     spa      |
                                                   |                     |              |
                                                   |                     +--------------+
                                                   |
                                                   |
+--------------+                         +---------+----+
|              |     1发送请求           |              | <---------------------------+
|    浏览器    +------------------------>+    nginx     |                             |
|              |                         |              +-----------------------+     |
+--------------+                         +-+----+-------+                       |     |
                                           |    ^                               |     |
                                           |    |                               |     |
                                           |    |                               |     |
                                           |    |                               |     |
                                           |    |                               |     |
                                           |    |                4未渲染的html  |     |   3模拟普通用户的访问
                2根据ua判断搜索引擎的爬虫   |    |                               |     |
                                           |    |                               |     |
                                           |    | 6返回渲染好的html             |     |
                                           |    |                               v     |
                                           |    |                         +-----------+--+
                                           |    +-------------------------+              |
                                           |                              |   seo_ssr    |
                                           +----------------------------->+              | +--------+
                                                                          +------------+-+          |
                                                                                       ^            | 5调用playwright渲染html
                                                                                       |            |
                                                                                       |            |
                                                                                       +------------+

```
