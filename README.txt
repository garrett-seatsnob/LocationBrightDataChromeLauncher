Location-Based Bright Data Residential Proxy Launcher

To install:
run make.py; it uses pyinstaller to install the program as a portable standalone
make.py path [bundle_type] [bw_ext_dir] [cfg_path]
    path: path to place the bundled files
    [bundle_type] (options: onefile, onedir) (default: onedir): how to bundle
can edit the lbdcl.bat file, once installed, to add/adjust default arguments to the run command
can edit the lbdcl.cfg file, once installed, to adjust some settings

To run:
-from python: run main.py cfg_dir ext_dir [--verbosity -v] [--proxy_mgr_addr] [--proxy_dummy_addr] [--proxy_dummy_port]
-from exe/dir: run main.exe cfg_dir ext_dir [--verbosity -v] [--proxy_mgr_addr] [--proxy_dummy_addr] [--proxy_dummy_port]
-from bat (easiest): run lbdcl.bat