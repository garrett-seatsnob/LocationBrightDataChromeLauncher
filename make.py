"""
Build a packaged folder or executable of the EvenueChromeLauncher
"""
import PyInstaller.__main__


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path')
    parser.add_argument('--exe', default=False, action='store_true')
    args = parser.parse_args()

    pyi_args = list()
    if args.exe:
        pyi_args.append('--onefile')
    pyi_args.append(f'--distpath {args.path}')
    pyi_args.append('main.py')

    PyInstaller.__main__.run(pyi_args)
