; 该脚本使用 HM VNISEdit 脚本编辑器向导产生

; 安装程序初始定义常量
!define PRODUCT_NAME "GBT_Tool"
!define PRODUCT_VERSION "0.1"
!define PRODUCT_PUBLISHER "Ghost"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\qt_run.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
!define MUI_ABORTWARNING
!define MUI_ICON "app_icon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; 语言选择窗口常量设置
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 许可协议页面
!insertmacro MUI_PAGE_LICENSE "NSIS_Licence.txt"
; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\qt_run.exe"
!insertmacro MUI_PAGE_FINISH

; 安装卸载过程页面
!insertmacro MUI_UNPAGE_INSTFILES

; 安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装预释放文件
!insertmacro MUI_RESERVEFILE_LANGDLL
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI 现代界面定义结束 ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "GBT Tool Installer.exe"
InstallDir "$PROGRAMFILES\GBT_Tool"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show
BrandingText "NSIS"

Section "主程序" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File /r "..\dist\qt_run.dist\*.*"
  CreateDirectory "$SMPROGRAMS\GBT_Tool"
  CreateShortCut "$SMPROGRAMS\GBT_Tool\GBT_Tool.lnk" "$INSTDIR\qt_run.exe"
  CreateShortCut "$DESKTOP\GBT_Tool.lnk" "$INSTDIR\qt_run.exe"
  File "..\dist\qt_run.dist\qt_run.exe"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\GBT_Tool\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\qt_run.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\qt_run.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

/******************************
 *  以下是安装程序的卸载部分  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\qt_run.exe"

  Delete "$SMPROGRAMS\GBT_Tool\Uninstall.lnk"
  Delete "$DESKTOP\GBT_Tool.lnk"
  Delete "$SMPROGRAMS\GBT_Tool\GBT_Tool.lnk"

  RMDir "$SMPROGRAMS\GBT_Tool"

  RMDir /r "$INSTDIR\zstandard"
  RMDir /r "$INSTDIR\vtkmodules"
  RMDir /r "$INSTDIR\src"
  RMDir /r "$INSTDIR\shiboken6"
  RMDir /r "$INSTDIR\pytz"
  RMDir /r "$INSTDIR\PySide6"
  RMDir /r "$INSTDIR\PIL"
  RMDir /r "$INSTDIR\pandas.libs"
  RMDir /r "$INSTDIR\pandas"
  RMDir /r "$INSTDIR\numpy.libs"
  RMDir /r "$INSTDIR\numpy"
  RMDir /r "$INSTDIR\matplotlib.libs"
  RMDir /r "$INSTDIR\matplotlib"
  RMDir /r "$INSTDIR\kiwisolver"
  RMDir /r "$INSTDIR\datatable"
  RMDir /r "$INSTDIR\contourpy"
  RMDir /r "$INSTDIR\charset_normalizer"
  RMDir /r "$INSTDIR\certifi"

  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "您确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从您的计算机移除。"
FunctionEnd
