project/
├── main.py
├── ui/
│   ├── main.ui
│   └── ... (其他UI文件，如对话框、子窗口等)
├── styles/
│   └── ... (qss样式)
├── resources/
│   ├── images/
│   │   ├── logo.png
│   │   └── ... (其他图片资源)
│   └── ... (其他资源文件)
├── models/
│   ├── __init__.py
│   └── data_model.py (数据模型的实现)
├── tool/
│   ├── __init__.py
│   └── main_controller.py (主控制器逻辑)
└── tests/
|   ├── test_main_window.py (MainWindow类的测试)
|    └── ... (其他测试用例或测试脚本)
└── AppPacket/
|    └── ... (打包编译的结果，直接拷贝到别的电脑即可运行)
└── build/
     └── ... (打包编译的过程文件)     

打包过程：1、vscode运行qt2py.py文件
          2、vscode运行build.py文件
          3、打包后的文件在文件夹中：AppPacket