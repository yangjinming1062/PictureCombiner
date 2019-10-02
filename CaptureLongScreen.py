from PIL import Image
from numpy import array
from glob import glob
from os import path
from scipy import stats
import sys
'''
将两张有重叠的图片拼接成一张长图，目标效果：123+234 →1234
'''

def _ComputerSimilar(A,B,similar,low,heigh):
    '''
    计算两个矩阵的相似度，如果认为相似则返回值为0，否则为非0值
    '''
    C = A - B
    CS = stats.mode(C.reshape(-1,3))
    if not CS[0][0].any() and (CS[1][0][0] > float(similar) * C.reshape(-1,3).shape[0]):#模糊之前也得保证超过similar成的像素点无差异
        C[(C <int(low)) | (C>int(heigh))] = 0
        return C.max()


def _FindBorder(imgA,imgB,similar,low,heigh,CombineType):
    '''
    对比发现两张图片的结合处应该在哪，imgA为主图，从imgB中查找不同的部分进行拼接
    imgA,imgB为Image打开后的图片，非文件路径，通过numpy转化成三维数组
    *一切运算的前提是认为AB图是可以拼接的，AB有重合则排除重合，没有则首尾相接
    '''
    a = array(imgA)
    b = array(imgB)
    if CombineType == 'H':#三个维度依次是(高，宽，RGB),如果水平对比则前两个轴需要调整，这样后面的都不需要变
        a = a.transpose((1,0,2))
        b = b.transpose((1,0,2))
    if a.shape[1] != b.shape[1]:
        return  #垂直拼接必须同宽的图片,水平拼接必须等高

    if a.shape[0] >= b.shape[0]:#A图不比B图短(窄)
        if _ComputerSimilar(a[-b.shape[0]:],b,similar,low,heigh) == 0:#全是0表示A已经包含B了，直接over
            return 0
    else:#B图更长(宽)则意味着肯定有A不包含的，那么从和A等长的部分往上
        if _ComputerSimilar(a,b[:a.shape[0]],similar,low,heigh) == 0:#B的头部和A一样，则交换AB就好了啊，此情况传特殊的-1
            return -1

    MaxValue = min(a.shape[0],b.shape[0])
    for i in range(1,MaxValue):#从1开始是因为0的情况在上面已经判断过了
        B = b[:MaxValue-i]#B图从下往上缩小范围
        A = a[-B.shape[0]:]#A图对应的从上往下缩小范围
        #if not (A - B).any():#AB对齐，找到了重合区，返回此时的分界位(这种需要的匹配度太强了，差一点点颜色就完蛋了
        # ，而实际上不知道为什么同一张图片裁剪出来的同位置在不同图片中RGB可能都会有差异，因此改为模糊计算法)
        if _ComputerSimilar(A,B,similar,low,heigh) == 0:#增加一点模糊化，针对单个像素点颜色
            return b.shape[0] - B.shape[0]
    
    return b.shape[0]#到最后都没有重合则首尾相接


def CombinePic(imgA,imgB,fileName,similar = 0.85,low = 50,heigh = 200,CombineType = 'V'):
    '''
    以A为主，在A的下面(右面)拼接上B图和A图不重合的部分，达到长图的目的
    '''
    a = Image.open(imgA).convert('RGB')
    b = Image.open(imgB).convert('RGB')

    b_value = _FindBorder(a,b,similar,low,heigh,CombineType)
    if b_value is None:
        return
    if b_value == -1:
        a.close()
        b.save(fileName)
        b.close()
        return
    if CombineType == 'V':
        img_new = Image.new('RGB',(a.width, a.height+b_value))
        rect = 0,b.height-b_value,b.width,b.height
        img_new.paste(b.crop(rect),(0,a.height))
    else:
        img_new = Image.new('RGB',(a.width+b_value, a.height))
        rect = b_value,b.height,b.width,b.height
        img_new.paste(b.crop(rect),(a.width,0))
    img_new.paste(a,(0,0))
    a.close()
    b.close()
    img_new.save(fileName)
    img_new.close()


def DirCombine(dirPath,fileName = 'temp.jpg',picType = '*',similar = 0.85,low = 50,heigh = 200,CombineType = 'V'):
    '''
    讲文件夹内图片一张张按顺序拼接
    dirPath：路径；fileName:合成后的长图的名称；picType文件夹内待拼接文件类型
    similar：区域绝对相似度，（0,1]取值越接近1越严格；low：单颜色噪点最小值上限，差值小于该值认为无差异，取值[0,255]；heigh：大于该值认为无差异[0,255]
    CombineType:拼接类型，垂直（上到下）拼接V,水平（左到右）拼接H
    '''
    fileList = glob(path.join(dirPath,"*.%s"%picType))#这里应该保证图片按顺序排列好
    if len(fileList) < 2:
        return
    CombinePic(fileList[0],fileList[1],fileName,similar,low,heigh,CombineType)#先拿出来前两张生成初始目标图
    for img in fileList[2:]:#一张张追加长度
        CombinePic(fileName,img,fileName,similar,low,heigh,CombineType)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        eval(sys.argv[1:]+str(tuple(sys.argv[2:])))#eval('DirCombine(A,B)')等效于执行DirCombine(A,B)
    else:
        DirCombine("")
    print('拼接完成')