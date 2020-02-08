"""
公式模块
"""

import os, re
from excel.xlrd import open_workbook
from excel.xlutils.copy import copy


def scrd_spliter(rd_list_file, rd_list_data, save_template_file, save_template_begindex, save_dir):
    """
    生存认定分组
    """
    sheet_read = open_workbook(rd_list_file).sheet_by_index(0)
    
    for xz, xz_data in rd_list_data.items():
        print(xz)
        # 读取数据索引
        xz_reg = xz_data[0]
        pos_list = xz_data[1]
        cz_data_map = {}
        for pos in pos_list:
            for row in range(*pos):
                xz_cz = sheet_read.row_values(row-1)[0]
                m = re.search(xz_reg, xz_cz)
                if m:
                    cz = m.group()
                    if cz_data_map.get(cz):
                        cz_data_map[cz].append(row-1)
                    else:
                        cz_data_map[cz] = [row-1]
                        
        # 创建乡镇目录
        xz_save_dir = os.path.join(save_dir, xz)
        if not os.path.exists(xz_save_dir):
            os.mkdir(xz_save_dir)

        # 生成乡镇文件
        for cz, cz_data in cz_data_map.items():
            print('  ' + cz)
            book_write = copy(open_workbook(save_template_file, formatting_info=1))
            sheet_write = book_write.get_sheet(0)
            rowindex = begindex = save_template_begindex
            sheet_write.update(1, 0, '  单位名称：'+cz)
            
            for i in cz_data:
                xzqh = sheet_read.row_values(i)[0]
                idcard = sheet_read.row_values(i)[1]
                name = sheet_read.row_values(i)[2]
                jfnd = sheet_read.row_values(i)[3]
                gjje = sheet_read.row_values(i)[4]
                djje = sheet_read.row_values(i)[5]
                jffs = sheet_read.row_values(i)[6]
                if rowindex > begindex:
                    sheet_write.insert_row(rowindex)
                    sheet_write.copy_row_style(begindex, rowindex)
                sheet_write.update(rowindex, 0, rowindex-begindex+1)
                sheet_write.update(rowindex, 1, xzqh)
                sheet_write.update(rowindex, 2, name)
                sheet_write.update(rowindex, 3, idcard)
                sheet_write.update(rowindex, 4, jfnd)
                sheet_write.update(rowindex, 5, gjje)
                sheet_write.update(rowindex, 6, djje)
                sheet_write.update(rowindex, 7, jffs)
                rowindex += 1

            book_write.save(os.path.join(xz_save_dir, cz[len(xz):]+'.xls'))


if __name__ == '__main__':
    import collections
    rd_list_data = collections.OrderedDict([
        ('城正街街道办事处', ('城正街街道办事处.+社区', [(3370, 3694)])),
        #('广场街道办事处'  , ('广场街道办事处.+社区',   [(3694, 3884)])),
        #('鹤岭镇'          , ('鹤岭镇.+村|鹤岭镇.+社区', [(3884, 4414)])),
        #('姜畲镇'          , ('姜畲镇.+村|姜畲镇.+?居委会', [(4414, 19793)])),
        #('楠竹山镇'        , ('楠竹山镇.+村|楠竹山镇.+社区', [(19793, 20291)])),
        #('平政路街道办事处', ('平政路街道办事处.+社区', [(20291, 20449)])),
        #('万楼街道办事处'  , ('万楼街道办事处.+村|万楼街道办事处政府机关', [(20449, 20530)])),
        #('先锋街道办事处'  , ('先锋街道办事处.+村|先锋街道办事处农场|先锋街道办事处政府机关', [(20530, 21477)])),
        #('响塘镇'          , ('响塘镇.+村|响塘镇.+?居委会|响塘镇政府机关', [(21477, 41838)])),
        #('羊牯塘街道办事处', ('羊牯塘街道办事处.+社区', [(41838, 41908)])),
        #('窑湾街道办事处'  , ('窑湾街道办事处.+社区',   [(41908, 42149)])),
        #('雨湖路街道办事处', ('雨湖路街道办事处.+社区', [(42149, 42341)])),
        #('云塘街道办事处'  , ('云塘街道办事处.+社区',   [(42341, 42715)])),
        #('长城乡'          , ('长城乡.+?村|长城乡政府机关', [(2, 3370)])),
        #('昭潭街道办事处'  , ('昭潭街道办事处.+村|昭潭街道办事处.+社区', [(42715, 42951)])),
        #('中山路街道办事处', ('中山路街道办事处.+社区', [(42951, 43251)])),
    ])
    scrd_spliter('D:\\缴费公示\\2016年度居保缴费20170214.xls',
                 rd_list_data,
                 'D:\\缴费公示\\雨湖区居保缴费公示花名册 - 模板.xls', 3,
                 'D:\\缴费公示\\2016年雨湖区城乡居保缴费公示')
    
    
