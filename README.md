# 无人机搭载系统对应开发软件
此项目使用pdm作为虚拟环境管理器。

### 运行
```bash
pdm install --lockfile=py312-win.lock
pdm run PySideApp
```

### 手动构建
```bash
pdm build
```

### gitea编译说明
 - 如本项目需使用`gitea CI`构建，请在提交git更改（commit）后，对需要构建的commit右键添加一个以w结尾的标签（release则添加一个以v开头的标签），再进行包含标签的推送（pycharm中则对应推送页面勾选“推送标记：所有”），以对应workflow文件中描述的触发条件。