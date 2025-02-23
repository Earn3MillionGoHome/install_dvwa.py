#!/usr/bin/env python3
import subprocess
import os
import sys

# ---------------------------
# 颜色输出函数
# ---------------------------
def print_success(message):
    """以绿色打印成功提示信息"""
    print(f"\033[32m{message}\033[0m")

def print_error(message):
    """以红色打印错误信息"""
    print(f"\033[31m{message}\033[0m")

def print_info(message):
    """以青色打印提示信息"""
    print(f"\033[36m{message}\033[0m")

# ---------------------------
# 执行命令函数
# ---------------------------
def run_command(cmd, shell=False, input_text=None, env=None, success_msg=None):
    """
    执行命令并捕获输出，成功后打印绿色提示，失败时打印红色错误信息并抛出异常。
    """
    cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
    print_info(f"执行命令: {cmd_str}")
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            input=input_text.encode() if input_text else None,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        if result.stdout:
            print("输出: " + result.stdout.decode().strip())
        if success_msg:
            print_success(success_msg)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行出错: {cmd_str}")
        if e.stdout:
            print_error("标准输出: " + e.stdout.decode().strip())
        if e.stderr:
            print_error("错误输出: " + e.stderr.decode().strip())
        raise

# ---------------------------
# 手动配置说明
# ---------------------------
def print_manual_instructions():
    instructions = """
【DVWA 手动配置教程】
1. 请访问 https://github.com/digininja/DVWA 或 https://dvwa.co.uk 下载最新的 DVWA 源代码包。
2. 将下载的 DVWA 文件解压到 /var/www/html/dvwa 目录（确保该目录存在且 Apache 用户有权限访问）。
3. 修改 DVWA 目录权限：
   sudo chown -R www-data:www-data /var/www/html/dvwa
4. 复制配置文件：
   cp /var/www/html/dvwa/config/config.inc.php.dist /var/www/html/dvwa/config/config.inc.php
5. 编辑 /var/www/html/dvwa/config/config.inc.php，根据你的 MySQL 用户和密码进行调整。
6. 使用 MySQL 创建 DVWA 数据库和用户（例如：数据库名: dvwa, 用户: dvwa, 密码: dvwa）。
7. 启用 Apache 的 mod_rewrite 模块，并重启 Apache 服务：
   sudo a2enmod rewrite
   sudo systemctl restart apache2
8. 通过浏览器访问 http://your_server_ip/dvwa 进行 DVWA 的 Web 配置和初始化。
    """
    print_success(instructions)

# ---------------------------
# Git 克隆函数（带重试机制）
# ---------------------------
def git_clone_with_fallback(repo_url, dest_dir):
    """
    尝试克隆 DVWA 仓库，如果失败则设置环境变量 GIT_SSL_NO_VERIFY=1 重新尝试，
    若重试仍失败，则提示用户手动下载并输出后续配置教程。
    """
    try:
        run_command(["git", "clone", repo_url, dest_dir], success_msg="克隆 DVWA 仓库完成")
    except Exception:
        print_error("检测到 git clone 失败，尝试使用 GIT_SSL_NO_VERIFY=1 重试...")
        env = os.environ.copy()
        env["GIT_SSL_NO_VERIFY"] = "1"
        try:
            run_command(["git", "clone", repo_url, dest_dir], env=env,
                        success_msg="克隆 DVWA 仓库完成（使用 GIT_SSL_NO_VERIFY）")
        except Exception:
            print_error("重试失败。如果仍无法下载 DVWA，请手动下载。")
            print_manual_instructions()
            sys.exit(1)

# ---------------------------
# 主函数
# ---------------------------
def main():
    # 检查是否以 root 权限运行
    if os.geteuid() != 0:
        print_error("请以 root 用户或使用 sudo 执行此脚本！")
        sys.exit(1)

    try:
        # 更新软件包列表
        run_command(["apt", "update"], success_msg="更新软件包列表完成")

        # 安装所需组件
        packages = [
            "apache2",
            "php",
            "php-mysql",
            "php-cli",
            "php-gd",
            "libapache2-mod-php",
            "git",
            "mysql-server"
        ]
        run_command(["apt", "install", "-y"] + packages, success_msg="安装 DVWA 所需组件完成")

        # 克隆 DVWA 仓库到指定目录
        dvwa_path = "/var/www/html/dvwa"
        if not os.path.exists(dvwa_path):
            git_clone_with_fallback("https://github.com/digininja/DVWA.git", dvwa_path)
        else:
            print_success("检测到 DVWA 目录已存在，跳过克隆步骤。")

        # 修改 DVWA 目录权限
        run_command(["chown", "-R", "www-data:www-data", dvwa_path],
                    success_msg="修改 DVWA 目录权限完成")

        # 复制默认配置文件
        config_dist = os.path.join(dvwa_path, "config/config.inc.php.dist")
        config_file = os.path.join(dvwa_path, "config/config.inc.php")
        if not os.path.exists(config_file):
            run_command(["cp", config_dist, config_file], success_msg="拷贝 DVWA 配置文件完成")
        else:
            print_success("检测到 DVWA 配置文件已存在，跳过拷贝步骤。")

        # 创建 MySQL 数据库和用户
        mysql_commands = """
CREATE DATABASE IF NOT EXISTS dvwa;
CREATE USER IF NOT EXISTS 'dvwa'@'localhost' IDENTIFIED BY 'dvwa';
GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';
FLUSH PRIVILEGES;
"""
        run_command(["mysql", "-u", "root"], input_text=mysql_commands,
                    success_msg="MySQL 数据库和用户创建完成")

        # 启用 Apache mod_rewrite 模块
        run_command(["a2enmod", "rewrite"], success_msg="启用 Apache mod_rewrite 模块完成")

        # 重启 Apache 服务
        run_command(["systemctl", "restart", "apache2"], success_msg="Apache 重启完成")

        print_success("DVWA 安装完成！请通过浏览器访问 http://your_server_ip/dvwa 进行后续配置。")
    except Exception as e:
        print_error("安装过程中发生异常: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
