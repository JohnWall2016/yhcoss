
class NumUtils:

    @classmethod
    def to_chinese_number(cls, number):
        """
        将数字转换为中文大写
        """
        bign = {1:'壹',2:'贰',3:'叁',4:'肆',5:'伍',
                6:'陆',7:'柒',8:'捌',9:'玖',0:'零'}
        place = ['','拾','佰','仟','万']
        unit = ['元','角','分']
        whole = '整'
        yi = '亿'

        def whole_part_to_chinese(wnumber):
            ybase = 10 ** 8
            ypart = ''
            if wnumber > ybase:
                ypart = whole_part_to_chinese(wnumber//ybase)
                wnumber %= ybase

            ret = ''
            zerop = False
            for i in range(7, -1, -1):
                base = 10 ** i
                if wnumber//base > 0:
                    if zerop:
                        ret += bign[0]
                    #print(wnumber, base)
                    ret += bign[wnumber//base] + place[i%4]
                    zerop = False
                elif wnumber//base == 0 and ret:
                    zerop = True
                if i == 4 and ret:
                    ret += place[4]
                wnumber = wnumber % base
                if wnumber == 0 and i != 0:
                    zerop = True
                    break

            if ypart:
                ret = ypart[0] + yi + ret

            return (ret, zerop)
                
        snum = '%.2f' % number
        wnum, dnum = snum.split('.')
        wnum = int(wnum)
        dnum = int(dnum)

        chnnum, zerop = whole_part_to_chinese(wnum)
        chnnum += unit[0]

        if dnum == 0:
            chnnum += whole
        elif dnum % 10 == 0:
            if zerop:
                chnnum += bign[0]
            chnnum += bign[dnum//10] + unit[1] + whole
        else:
            if zerop or dnum//10 == 0:
                chnnum += bign[0]
            if dnum//10 != 0:
                chnnum += bign[dnum//10]
            if dnum//10 > 0:
                chnnum += unit[1]
            chnnum += bign[dnum % 10] + unit[2]
        
        return chnnum


class StrUtils:
    @classmethod
    def locale_compare(cls, s1, s2):
        import locale
        locale.setlocale(locale.LC_COLLATE, 'zh_CN.UTF8')
        return locale.strcoll(s1, s2)
    

if __name__ == '__main__':
    #print(NumUtils.to_chinese_number(11111111111110.11))
    #print(NumUtils.to_chinese_number(2932475.37))
    print(StrUtils.locale_compare('中山路', '楠竹山'))
    print(StrUtils.locale_compare('中山路', '昭潭'))
