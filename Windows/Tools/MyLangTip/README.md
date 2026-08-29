# windows_tool_MyLangTip
微軟注音顯示小工具

功能: Windoes OS 中在指標附近顯示"微軟注音"現在的模式

開啟: 點擊 dist/MyLangTip.exe

關閉: 從工作管理員找到 MyLangTip 並關閉

---------------------------------------------

修改程式

程式: 
./main.py

打包:
```bash
pyinstaller --noconsole --onefile --clean --name "MyLangTip" main.py
```
