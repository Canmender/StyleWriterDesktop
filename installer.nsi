; StyleWriter Desktop 安装程序
; 使用 NSIS 编译

!include "MUI2.nsh"

; 安装程序名称
Name "StyleWriter Desktop"
OutFile "dist\StyleWriter-Setup.exe"
InstallDir "$PROGRAMFILES\StyleWriter"
RequestExecutionLevel admin

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "app\icon.ico"

; 页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "SimpChinese"

Section "安装"
  SetOutPath "$INSTDIR"
  
  ; 复制文件
  File /r "build\installer\*.*"
  
  ; 创建快捷方式
  CreateDirectory "$SMPROGRAMS\StyleWriter"
  CreateShortCut "$SMPROGRAMS\StyleWriter\StyleWriter.lnk" "$INSTDIR\StyleWriter.bat"
  CreateShortCut "$DESKTOP\StyleWriter.lnk" "$INSTDIR\StyleWriter.bat"
  
  ; 写入卸载信息
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; 写入注册表
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "DisplayName" "StyleWriter Desktop"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
SectionEnd

Section "卸载"
  ; 删除文件
  RMDir /r "$INSTDIR"
  
  ; 删除快捷方式
  RMDir /r "$SMPROGRAMS\StyleWriter"
  Delete "$DESKTOP\StyleWriter.lnk"
  
  ; 删除注册表
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter"
SectionEnd

