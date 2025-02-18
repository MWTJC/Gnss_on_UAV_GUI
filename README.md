# PySide6-Nuitka-template
此模板使用pdm作为虚拟环境管理器。

使用说明
### 请勿将修改上传到本模板仓库
 - gitea页面中，通过点击“使用此模板”创建对应的仓库
 - 在ide中通过vcs导入创建的仓库
 - 使用下面的命令建立虚拟环境并指定python版本
   ```bash
   pdm use 3.12
   ```
 - 修改`pyproject.toml`中的信息并`pdm lock --lockfile=py312-win.lock`
 - 使用下面的命令安装依赖环境
   ```bash
   pdm install --lockfile=py312-win.lock
   ```
 - pycharm中，可双击`\build_src\ui`中的ui文件进行修改
 - 在`.\scripts`中运行一次`regen_ui.py`(后续每次更新ui文件都需要运行一次这个文件才能看到效果)
 - 运行`main_run.py`
 - Enjoy.
### gitea编译说明
 - 如本项目需使用`gitea CI`构建，请在提交git更改（commit）后，对需要构建的commit右键添加一个以w结尾的标签，再进行包含标签的推送（pycharm中则对应推送页面勾选“推送标记：所有”），以对应workflow文件中描述的触发条件。