# mm_erp

## 克隆项目 在pycharm里使用从vcs获取
```angular2html
https://user:glpat-Va3mXhAb9QQCiPmn_NBH@git.tongji.edu.cn/mm_team/mm_erp.git
```
## 配置环境
```angular2html
1. conda create --name test2 python==3.10
2. conda activate test2
3. pip install Django
4. pip install pymysql
5. pip install pytz
6. pip install pandas
7. python manage.py runserver
```
在浏览器中打开[http://127.0.0.1:8000/](http://127.0.0.1:8000/)即可自动跳转登录页面；
<br>

测试账号：admin@tongji.edu.cn
<br>
密码：Admin

管理员账号：test<br>
密码：test

已基本解决：<br>
1、创建供应商<br>
2、查询供应商<br>
3、更新供应商信息<br>

待解决问题：<br>
1、需确定哪些字段为必要（电话和传真，如果填了需要判断其数据规范性。目前display中电话不能为空，其余皆可以为空；create中电话、传真、街区地址、支付类型、交易货币可以为空）<br>
2、display页面中若电话和传真在库中无数据则变成了None，我希望它为空值。<br>
3、供应商名称vname可以重复，create时直接给出警告信息alert<br>