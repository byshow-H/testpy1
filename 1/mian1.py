import os
import subprocess
import re
import shutil


def is_git_installed():
    """检查系统是否安装了Git"""
    try:
        subprocess.check_output(['git', '--version'], stderr=subprocess.STDOUT)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def validate_github_url(url):
    """验证GitHub仓库URL是否有效"""
    patterns = [
        r'^https?://github\.com/[\w-]+/[\w-]+\.git$',
        r'^git@github\.com:[\w-]+/[\w-]+\.git$',
        r'^https?://github\.com/[\w-]+/[\w-]+$'
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False


def normalize_github_url(url):
    """标准化GitHub URL为.git格式"""
    if url.endswith('.git'):
        return url
    return f"{url}.git"


def clone_github_repo(repo_url, temp_dir):
    """克隆GitHub仓库到临时目录"""
    if not is_git_installed():
        print("错误: 未检测到Git。请先安装Git并确保它在系统PATH中。")
        return False

    if not validate_github_url(repo_url):
        print(f"错误: 无效的GitHub仓库URL: {repo_url}")
        return False

    normalized_url = normalize_github_url(repo_url)

    try:
        print(f"正在克隆仓库: {normalized_url}")
        subprocess.run(
            ['git', 'clone', normalized_url, temp_dir],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"克隆失败: {e.stderr}")
        return False
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return False


def should_include_file(file_path, repo_root):
    """判断是否应该包含该文件"""
    # 相对路径
    rel_path = os.path.relpath(file_path, repo_root)

    # 排除版本控制相关文件和目录
    if '.git' in rel_path.split(os.sep):
        return False

    # 排除常见的依赖目录
    exclude_dirs = ['node_modules', 'venv', 'env', 'dist', 'build', 'target']
    for dir_name in exclude_dirs:
        if dir_name in rel_path.split(os.sep):
            return False

    # 排除大型二进制文件类型（可根据需要调整）
    binary_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
        '.zip', '.tar', '.gz', '.7z', '.rar',
        '.exe', '.dll', '.so', '.dylib',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
    ]
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext in binary_extensions:
        return False

    # 排除过大的文件（超过1MB）
    try:
        if os.path.getsize(file_path) > 1 * 1024 * 1024:
            return False
    except:
        return False

    return True


def traverse_and_collect(repo_dir, output_file):
    """遍历仓库目录并将代码收集到输出文件"""
    with open(output_file, 'w', encoding='utf-8', errors='ignore') as out_f:
        # 遍历所有文件和目录
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                file_path = os.path.join(root, file)

                # 检查是否应该包含该文件
                if not should_include_file(file_path, repo_dir):
                    continue

                try:
                    # 写入文件路径作为分隔符
                    rel_path = os.path.relpath(file_path, repo_dir)
                    out_f.write(f"\n\n{'=' * 80}\n")
                    out_f.write(f"文件路径: {rel_path}\n")
                    out_f.write(f"{'=' * 80}\n\n")

                    # 读取并写入文件内容
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as in_f:
                        content = in_f.read()
                        out_f.write(content)

                    print(f"已处理: {rel_path}")

                except Exception as e:
                    print(f"处理文件时出错 {file_path}: {str(e)}")


def main():
    # 获取用户输入
    github_url = input("请输入GitHub仓库URL: ").strip()
    output_filename = input("请输入输出文本文件名(默认: repo_code.txt): ").strip() or "repo_code.txt"

    # 创建临时目录
    repo_name = re.sub(r'[^a-zA-Z0-9_]', '_', github_url.split('/')[-1].replace('.git', ''))
    temp_dir = os.path.join(os.getcwd(), f"temp_{repo_name}")

    try:
        # 克隆仓库
        if not clone_github_repo(github_url, temp_dir):
            return

        # 检查临时目录是否存在
        if not os.path.isdir(temp_dir):
            print("错误: 仓库克隆失败，临时目录不存在")
            return

        # 遍历并收集代码
        print(f"开始收集代码到 {output_filename}...")
        traverse_and_collect(temp_dir, output_filename)

        print(f"\n代码收集完成！所有代码已保存到 {output_filename}")

    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            print(f"清理临时文件...")
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
