a = 'tim'
b = a
a += 'e'
print(b)
c = ['t', 'i', 'm']
d = c
c += ['e']
print(d)
a = [1, 2, 3, 4, 5]
print(a[2:4])
print(a[-2:])
print(a[::2])
def foo(a_int, b_list, c_list):
    a_int = a_int + 1
    b_list.append(1)
    c_list = c_list + [1]
a_int = 5
b_list = [5]
c_list = [5]
foo(a_int, b_list, c_list)
print(a_int, b_list, c_list)

foo = ['c', 'h', 'e', 'b', 'w', 'e', 'c', 's']
bar = {'h', 'b', 'c', 'n'}
foo = set([x for x in foo if foo.count(x) > 1])
bar = bar.intersection(foo)
print(bar)
def fibon(n):
    a = b = 1
    for i in range(n):
        yield a
        a, b = b, a + b
for item in fibon(5):
    print(item)

def foo(a, b='commit', *c, **d):
    print(a, b, c, d)
foo(1, z='merge', b='clone', x=6, y=7)
foo(1, 2, 'push', 5, x='pull', y='chekcout')

foo = [1, 2, 3, 4]
print(list(map(lambda x: x * x, foo)))
print(list(filter(lambda x: x % 2 == 0, foo)))

class Parent(object):
    x = 1
class Child1(Parent):
    def __str__(self):
        return str(self.x * 2)
class Child2(Parent):
    def __str__(self):
        return str(len(self))
    def __len__(self):
        return self.x * 3
c1 = Child1()
c2 = Child2()
print(Parent.x, Child1.x, Child2.x, c1, c2)
Child1.x = 2
print(Parent.x, Child1.x, Child2.x, c1, c2)
Parent.x = 3
print(Parent.x, Child1.x, Child2.x, c1, c2)

class makeHtmlTag(object):
    def __init__(self, tag):
        self.tag = tag
    def __call__(self, fn):
        def wrapped():
            return "<" + self.tag + ">" + fn() + "</" + self.tag + ">"
        return wrapped
@makeHtmlTag('b')
@makeHtmlTag('i')
def hello():
    return "hello world"
print(hello())

def func1():
    try:
        return 1
    except:
        return 2
    finally:
        print(3)
def func2():
    try:
        raise ValueError()
        return 1
    except:
        return 2
    finally:
        print(3)
print(func1())
print(func2())

a='2020-05-16 19:20:34|user.login|name=Charles&location=Beijing&device=iPhone'
e=a.split('|')[2].split('&')
print(e)
b=a.split('|')
c=b[2]
d=c.split('&')
print(d)
my_dict={}
for i in d:
    key,value = i.split('=')
    my_dict[key]=value
print(my_dict)


def binary_search(li):
    if li[0] >= 0:
        return li[0]
    elif li[-1] <= 0:
        return li[-1]
    else:
        left, right = 0, len(li) - 1
        while left < right:
            mid = (left + right) // 2
            if li[mid] <= 0 and li[mid + 1] > 0:
                if abs(li[mid]) < abs(li[mid + 1]):
                    return li[mid]
                else:
                    return li[mid - 1]
            elif li[mid] > 0:
                right = mid - 1
            elif li[mid] < 0:
                left = mid + 1


li = [-17, -12, 18, -3, -1, 0, 2, 5, 6, 7]
print(li)
a = binary_search(li)
print(a)


a=[1,5,2,9,8,0,6]
def quick_sort(test_list):
    less_list = []
    pivot_list = []
    more_list = []

    # 递归出口
    if len(test_list) <= 1:
        return test_list
    else:
        # 选定基准
        pivot = test_list[0]

        for i in test_list:
            # 将比基准小的值放入less队列
            if i < pivot:
                less_list.append(i)
            # 将比基准大的值放入more队列
            elif i > pivot:
                more_list.append(i)
            else:
                pivot_list.append(i)
        # 对less数列和more数列进行排序
        less_list = quick_sort(less_list)
        more_list = quick_sort(more_list)

        return less_list + pivot_list + more_list

b=quick_sort(a)
mid=(len(b)-1 )//2
print(mid)
print(b[mid])