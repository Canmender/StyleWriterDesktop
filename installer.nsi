; StyleWriter Desktop 安装程序
; 使用 NSIS 编译

!include "MUI2.nsh"
!include "FileFunc.nsh"

; ========== 基本信息 ==========
Name "StyleWriter Desktop"
OutFile "dist\StyleWriter-Setup.exe"
InstallDir "$LOCALAPPDATA\StyleWriter"
InstallDirRegKey HKCU "Software\StyleWriter" ""
RequestExecutionLevel user

; ========== 图标 ==========
;!define MUI_ICON "app\icon.ico"
;!define MUI_UNICON "app\icon.ico"

; ========== 界面设置 ==========
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "欢迎安装 StyleWriter Desktop"
!define MUI_WELCOMEPAGE_TEXT "StyleWriter Desktop 是一款风格化文章生成器。\r\n\r\n功能特点：\r\n  - 智能体 RAG 检索\r\n  - 本地模型推理 (llama.cpp)\r\n  - 云端 API 调用\r\n  - 数据清洗\r\n\r\n点击下一步继续安装。"

!define MUI_FINISHPAGE_RUN "$INSTDIR\StyleWriter.bat"
!define MUI_FINISHPAGE_RUN_TEXT "启动 StyleWriter Desktop"

; ========== 页面 ==========
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ========== 语言 ==========
!insertmacro MUI_LANGUAGE "SimpChinese"

; ========== 安装段 ==========
Section "安装"
  SetOutPath "$INSTDIR"
  
  ; 复制所有文件
  File /r "build\installer\*.*"
  
  ; 创建快捷方式
  CreateDirectory "$SMPROGRAMS\StyleWriter"
  CreateShortCut "$SMPROGRAMS\StyleWriter\StyleWriter.lnk" "$INSTDIR\StyleWriter.bat" "" "$INSTDIR\StyleWriter.bat" 0
  CreateShortCut "$DESKTOP\StyleWriter.lnk" "$INSTDIR\StyleWriter.bat" "" "$INSTDIR\StyleWriter.bat" 0
  
  ; 写入注册表
  WriteRegStr HKCU "Software\StyleWriter" "" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "DisplayName" "StyleWriter Desktop"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "DisplayIcon" "$INSTDIR\StyleWriter.bat"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                   "Publisher" "StyleWriter"
  
  ; 创建卸载程序
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; 获取安装大小
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter" \
                     "EstimatedSize" "$0"
SectionEnd

; ========== 卸载段 ==========
Section "卸载"
  ; 删除文件
  RMDir /r "$INSTDIR"
  
  ; 删除快捷方式
  RMDir /r "$SMPROGRAMS\StyleWriter"
  Delete "$DESKTOP\StyleWriter.lnk"
  
  ; 删除注册表
  DeleteRegKey HKCU "Software\StyleWriter"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\StyleWriter"
SectionEnd

