"""
认定模块
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
                else:
                    raise Exception(xz_cz)
                        
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
            sheet_write.update(1, 0, '填报单位（公章）：'+cz)
            
            for i in cz_data:
                xzqh = sheet_read.row_values(i)[0]
                name = sheet_read.row_values(i)[1]
                idcard = sheet_read.row_values(i)[2]
                if rowindex > begindex:
                    sheet_write.insert_row(rowindex)
                    sheet_write.copy_row_style(begindex, rowindex)
                sheet_write.update(rowindex, 0, rowindex-begindex+1)
                sheet_write.update(rowindex, 1, xzqh)
                sheet_write.update(rowindex, 2, name)
                sheet_write.update(rowindex, 3, idcard)
                rowindex += 1

            book_write.save(os.path.join(xz_save_dir, cz[len(xz):]+'.xls'))


if __name__ == '__main__':
    import collections
    rd_list_data = collections.OrderedDict([
        ('城正街街道办事处', ('城正街街道办事处.+社区', [(2, 186)])),
        ('广场街道办事处'  , ('广场街道办事处.+社区',   [(186, 267)])),
        ('鹤岭镇'          , ('鹤岭镇.+村|鹤岭镇.+社区|鹤岭镇.+?居委会|鹤岭镇政府机关', [(267, 11441)])),
        ('姜畲镇'          , ('姜畲镇.+村|姜畲镇.+?居委会', [(11441, 20632)])),
        ('楠竹山镇'        , ('楠竹山镇.+村|楠竹山镇.+社区', [(20632, 20850)])),
        ('万楼街道办事处'  , ('万楼街道办事处.+村|万楼街道办事处.+社区|万楼街道办事处政府机关', [(20850, 20886)])),
        ('先锋街道办事处'  , ('先锋街道办事处.+村|先锋街道办事处.+社区|先锋街道办事处农场|先锋街道办事处政府机关', [(20886, 21071)])),
        ('窑湾街道办事处'  , ('窑湾街道办事处.+社区',   [(21071, 21360)])),
        ('雨湖路街道办事处', ('雨湖路街道办事处.+社区', [(21360, 21558)])),
        ('云塘街道办事处'  , ('云塘街道办事处.+社区',   [(21558, 21724)])),
        ('长城乡'          , ('长城乡.+?村|长城乡政府机关', [(21724, 24015)])),
        ('昭潭街道办事处'  , ('昭潭街道办事处.+村|昭潭街道办事处.+社区', [(24015, 24178)])),
    ])
    scrd_spliter('D:\\生存认定\\2017年\\区城乡居民基本养老保险待遇人员20171012.xls',
                 rd_list_data,
                 'D:\\生存认定\\2017年\\雨湖区居保资格认证花名册 - 模板.xls', 3,
                 'D:\\生存认定\\2017年\\2017年雨湖区城乡居保生存认定\\2017年度雨湖区城乡居民基本养老保险待遇领取人员资格认证花名册（表二）')
    
    
