# DVWA 自动安装脚本

该脚本用于在 Ubuntu 20.04 上自动安装和配置 [DVWA (Damn Vulnerable Web Application)](https://github.com/digininja/DVWA)。脚本自动完成以下任务：

- 更新系统软件包列表  
- 安装必要组件（Apache、PHP、MySQL、Git 等）  
- 从 GitHub 克隆 DVWA 仓库，并在克隆失败时尝试使用 `GIT_SSL_NO_VERIFY` 重试  
- 修改 DVWA 目录权限，确保 Apache 能够访问  
- 拷贝默认配置文件（从 `config.inc.php.dist` 到 `config.inc.php`）  
- 使用 MySQL 创建 DVWA 数据库和用户  
- 启用 Apache 的 mod_rewrite 模块并重启 Apache  
- 在每个步骤完成后以绿色显示成功信息，出错时以红色显示错误信息  
- 记录每个步骤的完成情况，并在脚本结束时输出详细的步骤完成摘要  
- 如果 DVWA 克隆失败（包括重试失败），将提示用户手动下载 DVWA，并输出后续手动配置说明

## 特性

- **全自动安装与配置**：自动完成系统更新、组件安装、仓库克隆、权限设置、数据库配置和服务重启。  
- **健壮的 Git 克隆策略**：当标准克隆失败时，自动重试并提供手动下载提示。  
- **彩色终端输出**：使用绿色显示成功提示，红色显示错误信息，青色显示提示信息，方便一目了然地跟踪安装进度。  
- **详细步骤摘要**：脚本执行结束时会输出所有完成的步骤摘要，让用户清楚了解哪些步骤已成功执行。  
- **手动配置教程**：在自动克隆失败时，提供详细的 DVWA 手动配置说明。

## 使用方法

1. **下载或克隆该仓库**

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository
