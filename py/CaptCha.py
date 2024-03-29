# -*- coding: utf-8 -*-
# @Author: Mehaei
# @Date:   2019-12-19 15:05:00
# @Last Modified by:   Mehaei
# @Last Modified time: 2019-12-20 15:39:18

from PIL import Image
import math
import os
import string

# 夹角公式
class VectorCompare(object):
    # 计算矢量大小
    # 计算平方和
    def magnitude(self, concordance):
        total = 0
        for word, count in concordance.items():
            total += count ** 2
        return math.sqrt(total)

    # 计算矢量之间的 cos 值
    def relation(self, concordance1, concordance2):
        topvalue = 0
        for word, count in concordance1.items():
            if word in concordance2:
                # 计算相乘的和
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))


class AmazonVerifyCode(object):
    def __init__(self):
        # 加载训练集
        self.vector = VectorCompare()
        self._loads_sample_data()

    def _loads_sample_data(self):
        iconset = list(string.ascii_lowercase)
        self.imageset = []
        for letter in iconset:
            ppath = '../iconset1/%s/' % (letter)
            if not os.path.exists(ppath):
                os.makedirs(ppath)
            for img in os.listdir(ppath):
                temp = []
                if img != "":
                    temp.append(self.buildvector(Image.open("../iconset1/%s/%s" % (letter, img))))
                self.imageset.append({letter: temp})

    # 将图片转换为矢量
    def buildvector(self, im):
        d1 = {}
        count = 0
        for i in im.getdata():
            d1[count] = i
            count += 1
        return d1

    def get_verify_code(self, item):
        try:
            newjpgname = []
            im = Image.open(item)
            print(item)
            # jpg不是最低像素，gif才是，所以要转换像素
            im = im.convert("P")

            # 打印像素直方图
            his = im.histogram()

            values = {}
            for i in range(0, 256):
                values[i] = his[i]

            # 排序，x:x[1]是按照括号内第二个字段进行排序,x:x[0]是按照第一个字段
            # temp = sorted(values.items(), key=lambda x: x[1], reverse=True)

            # 占比最多的10种颜色
            # for j, k in temp[:10]:
            #     print(j, k)
            # 255 12177
            # 0 772
            # 254 94
            # 1 40
            # 245 10
            # 12 9
            # 236 9
            # 243 9
            # 2 8
            # 6 8
            # 255是白底，0是黑色，可以打印来看看0和254

            # 获取图片大小，生成一张白底255的图片
            im2 = Image.new("P", im.size, 255)
            for y in range(im.size[1]):
                # 获得y坐标
                for x in range(im.size[0]):

                    # 获得坐标(x,y)的RGB值
                    pix = im.getpixel((x, y))

                    # 这些是要得到的数字
                    # 事实证明只要0就行，254是斑点
                    if pix == 0:
                        # 将黑色0填充到im2中
                        im2.putpixel((x, y), 0)
            # 生成了一张黑白二值照片
            # im2.show()

            # 纵向切割
            # 找到切割的起始和结束的横坐标
            inletter = False
            foundletter = False
            start = 0
            end = 0

            letters = []

            for x in range(im2.size[0]):
                for y in range(im2.size[1]):
                    pix = im2.getpixel((x, y))
                    if pix != 255:
                        inletter = True
                if foundletter == False and inletter == True:
                    foundletter = True
                    start = x

                if foundletter == True and inletter == False:
                    foundletter = False
                    end = x
                    letters.append((start, end))

                inletter = False
            # print(letters)
            # [(27, 47), (48, 71), (73, 101), (102, 120), (122, 147), (148, 166)]
            # 打印出6个点，说明能切割成6个字母，正确

            # 开始破解训练
            count = 0
            for letter in letters:
                # (切割的起始横坐标，起始纵坐标，切割的宽度，切割的高度)
                im3 = im2.crop((letter[0], 0, letter[1], im2.size[1]))

                guess = []
                # 将切割得到的验证码小片段与每个训练片段进行比较
                for image in self.imageset:
                    for x, y in image.items():
                        if len(y) != 0:
                            guess.append((self.vector.relation(y[0], self.buildvector(im3)), x))

                # 排序选出夹角最小的（即cos值最大）的向量，夹角越小则越接近重合，匹配越接近
                guess.sort(reverse=True)
                print("", guess[0])
                newjpgname.append(guess[0][1])
                count += 1

            # 得到拼接后的验证码识别图像
            newname = str("".join(newjpgname))
            print(newname)
            # os.rename(item, path + newname + ".jpg")
        except Exception as err:
            print(err)
            # 如果错误就记录下来
            file = open("../jpg/error.txt", "a")
            file.write("\n" + item)
            file.close()


if __name__ == '__main__':
    p = "/Users/msw/works/full_crawler/amazon/verify_img/aarebr.jpg"
    a = AmazonVerifyCode()
    a.get_verify_code(p)
    a.get_verify_code(p)

