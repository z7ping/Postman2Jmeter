import PyInstaller.__main__
import os
import sys

def build_exe():
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, 'src')

    # 检查主程序文件是否存在
    main_path = os.path.join(src_dir, 'main.py')
    if not os.path.exists(main_path):
        raise FileNotFoundError(f"找不到主程序文件: {main_path}")

    print(f"使用主程序文件: {main_path}")

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
        '--add-data', f'{os.path.join(src_dir, "templates.py")};.',
        f'--distpath={os.path.join(current_dir, "dist")}',
        f'--workpath={os.path.join(current_dir, "build")}',
        f'--specpath={os.path.join(current_dir, "build")}',
    ]

    # 如果存在图标文件，添加图标
    icon_path = os.path.join(current_dir, 'resources', 'icon.ico')
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')

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