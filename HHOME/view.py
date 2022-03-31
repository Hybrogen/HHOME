from django.shortcuts import HttpResponse
from django.http import JsonResponse

import json

def index(request):
   return HttpResponse('自定义一些文本')

def data(request):
   data = {'数据是这样返回的'：'通过一个解析成json的字典对象'}
   # 常用的httpResponse，在返回数据的时候需要把字典解析成json"字符串"并且指定返回的文本类型
   return HttpResponse(json.dumps(data), content_type='application/json')
   # 也可以使用HttpResponse的一个子类JsonResponse，记得在头文件里引入对应的类
   # 使用JsonResponse可以直接返回字典对象，而不用再通过json库进行转换
   return JsonResponse(data)
