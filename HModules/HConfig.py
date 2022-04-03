#-*- coding:utf-8 -*-

import os

class CONFIG(object):
    def __init__(self, oriFile: str, setFile: str, initData: dict = dict()):
        r"""
        Arguments:
        oriFile -- 原配置文件路径（字符串 str），配置文件最终保存到这个文件中
        setFile -- 重置配置文件路径（字符串 str），此文件会被用户手动修改，通常读取后会被删除
        initData -- 初始化数据（字典 dict 默认为 dict()），当系统刚刚运行的时候，如果原配置文件不存在则创建配置文件并写入初始配置数据
        """
        self.oriFile = oriFile
        self.setFile = setFile
        self.data = initData
        self.load()

    def check_ori(self) -> bool:
        return os.path.isfile(self.oriFile)

    def check_set(self) -> bool:
        return os.path.isfile(self.setFile)

    def reset(self) -> int:
        r"""
        此方法判断是否有【重置文件】，如果有则更新【源文件】和【配置数据】

        Return value / exceptions raised:
        - 返回一个整数 int 如果有更新数据，返回 1，如果没有返回 600  此数字作为模块运行延迟时间
        """
        haveReset = False
        if self.check_set():
            os.rename(self.setFile, self.oriFile)
            haveReset = True
        self.load()
        return 1 if haveReset else 600

    def load(self):
        r"""
        此方法用于加载配置文件中的配置数据，并更新到内存（类成员变量）中
        """
        if not self.check_ori():
            self.save()
        with open(self.oriFile, encoding='utf8'):
            self.data = json.loads(f.readline())

    def save(self):
        r"""
        此方法用于把内存中的配置文件保存到文件中离线
        """
        with open(self.oriFile, 'w', encoding='utf8'):
            f.readline(json.dumps(self.data))

    def get_data(self, queryFields: list = []):
        r"""
        此方法用于返回内存中的配置数据

        Arguments:
        queryFields -- 请求的字段，按照层级顺序获取

        Return value / exceptions raised:
        - 返回一个字典 dict 内容为内存中的数据
        """
        rdata = self.data
        for f in queryFields: rdata = rdata[f]
        return rdata

    def updata(self, field, data):
        r"""
        此方法用于更新字段
        - 如果数据不需要更新，则直接返回
        - 如果需要更新，则更新后保存到文件离线配置
        """
        if self.data.get(field, None) == data: return
        self.data[field] = data
        self.save()

if __name__ == '__main__':
    conf = CONFIG()

