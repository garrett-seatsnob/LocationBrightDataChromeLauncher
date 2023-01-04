"""
Build a packaged folder or executable of the EvenueChromeLauncher
"""
import PyInstaller.__main__
import shutil
import pathlib
import sys

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--bundle_type', default='onedir', choices=('onedir', 'onefile'))
    args = parser.parse_args()

    pyi_args = ['main.py', f'--{args.bundle_type}', '--distpath', args.path, '-y', '--clean', '--noconsole']
    PyInstaller.__main__.run(pyi_args)

    this_path = pathlib.Path('.')
    bw_ext_path = this_path / pathlib.Path('bw-ext')
    path = pathlib.Path(args.path)
    if args.bundle_type == 'onefile':
        dest = path
    else:
        dest = path / 'main'
    shutil.copytree(bw_ext_path, dest / 'bw-ext', dirs_exist_ok=True)
    shutil.copy(pathlib.Path('lbdcl.cfg'), dest / 'lbdcl.cfg')

    if sys.platform == 'win32':
        with open(path / 'lbdcl.bat', 'w') as f:
            if args.bundle_type == 'onefile':
                f.write(r'start /b main .\ .\bw-ext')
            else:
                f.write(r'start /b main\main main main\bw-ext')
    elif sys.platform == 'linux':
        # TODO
        raise OSError('Platform not supported')
    elif sys.platform == 'darwin':
        # TODO
        raise OSError('Platform not supported')
