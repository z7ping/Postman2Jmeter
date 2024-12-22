import PyInstaller.__main__
import os
import sys
import shutil

def build_exe():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src', 'Postman2Jmeter')
    
    # 添加src目录到Python路径
    sys.path.insert(0, os.path.join(current_dir, 'src'))

    # 检查主程序文件是否存在
    main_path = os.path.join(src_dir, 'main.py')
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"找不到主程序文件: {main_path}")

    print(f"使用主程序文件: {main_path}")

    # 检查资源文件夹
    resources_dir = os.path.join(src_dir, 'resources')
    if not os.path.exists(resources_dir):
        print(f"警告: 资源文件夹不存在: {resources_dir}")
        os.makedirs(resources_dir, exist_ok=True)
        print(f"已创建资源文件夹: {resources_dir}")

    # PyInstaller 配置
    args = [
        main_path,
        '--name=Postman2JMeter',
        '--windowed',
        '--onefile',
        '--clean',
        '--noconfirm',
        '--hidden-import=jinja2',
        '--hidden-import=PyQt5',
        '--hidden-import=Postman2Jmeter',
        '--hidden-import=Postman2Jmeter.gui',
        '--hidden-import=Postman2Jmeter.converter',
        '--hidden-import=Postman2Jmeter.templates',
        '--add-data', f'{src_dir};Postman2Jmeter',
        '--paths', os.path.join(current_dir, 'src'),
        '--debug=all',
    ]

    # 如果资源文件夹存在且不为空，添加资源文件
    if os.path.exists(resources_dir) and os.listdir(resources_dir):
        args.extend(['--add-data', f'{resources_dir};Postman2Jmeter/resources'])

    # 添加构建路径
    args.extend([
        f'--distpath={os.path.join(current_dir, "dist")}',
        f'--workpath={os.path.join(current_dir, "build")}',
        f'--specpath={os.path.join(current_dir, "build")}',
    ])

    # 如果存在图标文件，添加图标
    icon_path = os.path.join(resources_dir, 'icon.ico')
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    else:
        print(f"警告: 图标文件不存在: {icon_path}")

    print("开始打包...")
    print(f"参数: {' '.join(args)}")

    try:
        # 运行 PyInstaller
        PyInstaller.__main__.run(args)
        print("打包完成!")
    except Exception as e:
        print(f"打包失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    build_exe() 