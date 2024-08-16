from django.core.management.base import BaseCommand
from MM.models import Stock


class Command(BaseCommand):
    help = '批量插入Stock数据'

    def handle(self, *args, **kwargs):
        stocks = [
            Stock(name='GD00', companyCode='CN00', pOrg='CN00', pGrp='G00'),  # 佛山顺德基地
            Stock(name='AH01', companyCode='CN00', pOrg='CN00', pGrp='A00'),  # 安徽合肥基地
            Stock(name='GD02', companyCode='CN00', pOrg='CN00', pGrp='G00'),  # 广州南沙基地
            Stock(name='JS00', companyCode='CN00', pOrg='CN00', pGrp='J00'),  # 江苏淮安基地
            Stock(name='CQ00', companyCode='CN00', pOrg='CN00', pGrp='C00'),  # 重庆基地
            Stock(name='HB01', companyCode='CN00', pOrg='CN00', pGrp='H00'),  # 湖北荆州基地
            Stock(name='SX00', companyCode='CN00', pOrg='CN00', pGrp='S00'),  # 山西临汾基地
            Stock(name='HD00', companyCode='CN00', pOrg='CN00', pGrp='B00'),  # 河北邯郸基地
            Stock(name='JX00', companyCode='CN00', pOrg='CN00', pGrp='X00'),  # 江西贵溪基地
            Stock(name='BD00', companyCode='VN00', pOrg='AS00', pGrp='V00'),  # 越南平阳省基地
            Stock(name='SZ00', companyCode='EG00', pOrg='AF00', pGrp='E00'),  # 埃及苏伊士湾基地
            Stock(name='PA00', companyCode='BR00', pOrg='SA00', pGrp='R00'),  # 巴西波苏阿雷格里市基地
            Stock(name='TF00', companyCode='AR00', pOrg='SA00', pGrp='D00'),  # 阿根廷火地岛省基地
            Stock(name='MH00', companyCode='IN00', pOrg='AS00', pGrp='I00'),  # 印度马哈拉施特拉邦基地
            Stock(name='CB00', companyCode='TH00', pOrg='AS00', pGrp='T00'),  # 泰国春武里府基地
            Stock(name='SJ00', companyCode='US00', pOrg='AS00', pGrp='U00'),  # 美国圣荷西市基地
        ]

        Stock.objects.bulk_create(stocks)
        self.stdout.write(self.style.SUCCESS('成功插入所有Stock数据！'))
