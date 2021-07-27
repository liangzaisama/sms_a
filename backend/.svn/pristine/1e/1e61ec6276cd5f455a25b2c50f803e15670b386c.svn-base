"""sms后端项目打包文件

1.py -> pyc
2.排除不需要打包的文件
"""
import os
import re
import shutil

project_name = 'sms'
prod_project_name = project_name + '_compile'

src_dir = '/Users/lwl/Desktop/work/svn_/SMS/backend'
dst_dir = '/Users/lwl/Desktop/安防/pack/SMS/sms'
dst_path = '/Users/lwl/Desktop/安防/pack/SMS/'
cur_dir = os.path.dirname(os.path.abspath(__file__))

# 更新忽略文件
update_ignore_file_list = [
        # 静态文件，基本不变
        '*.pyc',
        '.idea',
        '__pycache__',
        '.DS_Store',
        'doc',
        'bin',
        'front_end_pc',
        'logs',
        'service',
        '.coveragerc',
        'static',
        'extra_apps',

        # 代码
        # 'manage.py',    # 启动文件
        'config.ini',     # 配置文件
        'migrations',     # 迁移文件
    ]

# 部署忽略文件
deploy_ignore_file_list = [
        '.idea',
        '__pycache__',
        '.DS_Store',
        'doc',
        '*.log*',
        'uwsgi.pid',
        '.coveragerc',
        'media',
        'cache',
    ]


def rmdirs(top):
    if os.path.exists(top):
        for root, dirs, files in os.walk(top, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(top)


def copy_pyc(path, dest_path):
    for fd in os.listdir(path):
        fd_abs = os.path.join(path, fd)

        if fd_abs.endswith('__pycache__'):
            for pyc in os.listdir(fd_abs):
                shutil.copy(os.path.join(fd_abs, pyc), dest_path)
                os.remove(os.path.join(fd_abs, pyc))
            os.removedirs(fd_abs)
            continue

        if os.path.isdir(fd_abs) and not fd_abs.endswith(('rely_package', 'rely_packages_linux')):
            os.mkdir(os.path.join(dest_path, fd))
            copy_pyc(fd_abs, os.path.join(dest_path, fd))

        if fd_abs.endswith('wsgi.py') or (os.path.isfile(fd_abs) and not fd_abs.endswith(('.py', '.pyc'))):
            shutil.copy(fd_abs, dest_path)


def replace_name(path):
    for fd in os.listdir(path):
        fd_abs = os.path.join(path, fd)

        if os.path.isfile(fd_abs) and fd_abs.endswith('.cpython-36.pyc'):
            new_name = re.sub(r'.cpython-36', '', fd)
            os.rename(fd_abs, os.path.join(path, new_name))

        if os.path.isdir(fd_abs):
            replace_name(fd_abs)


def copyfile(ignore_file_list):
    os.system(f'cd {dst_path};rm -rf sms*')
    shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(*ignore_file_list))


def compile_code(compile_name):
    # 项目目录
    project_path = dst_dir
    # 编译目录
    compile_path = dst_dir.replace(project_name, compile_name)

    os.system('python3 -m compileall %s' % project_path)
    rmdirs(compile_path)
    os.mkdir(compile_path)

    copy_pyc(project_path, compile_path)
    print('编译成功！')

    replace_name(compile_path)
    print('修改文件名成功！')
    print(f'生成文件 {compile_path}')

    return compile_path


def zip_project_file(project_path):
    """生成压缩文件"""
    file_path, file_name = os.path.split(project_path)
    print('压缩路径', file_path)
    print('压缩文件名', file_name)
    os.system(f'cd {file_path};zip -r {file_name}.zip {file_name}')


def main():
    # 部署代码复制
    copyfile(deploy_ignore_file_list)
    compile_path = compile_code(prod_project_name)
    # zip_project_file(compile_path)


if __name__ == '__main__':
    main()
