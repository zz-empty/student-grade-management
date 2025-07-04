from re import sub
from rich import table
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.repr import T
from rich.table import Table
from rich import box, style
import sys
import time
from datetime import datetime
from network import NetworkClient
from auth import AuthManager
from student_manager import StudentManager
from admin_student_manager import AdminStudentManager
from admin_account_manager import AdminAccountManager
from logger import setup_logger


class StudentManagementCLI:
    def __init__(self):
        self.console = Console()
        self.logger = setup_logger("cli")
        self.network = NetworkClient()
        self.auth = AuthManager(self.network)
        self.student_manager = StudentManager(self.network)
        self.admin_student_manager = AdminStudentManager(self.network)
        self.admin_account_manager = AdminAccountManager(self.network)
        self.current_user = None
        self.permission = None

    def clear_screen(self):
        """清屏函数（跨平台）"""
        if sys.platform == "win32":
            import os

            os.system("cls")
        else:
            print("\033c", end="")

    def show_header(self, title):
        """显示界面标题"""
        self.clear_screen()
        self.console.rule(f"[bold blue]{title}", style="blue")
        print()

    def connect_to_server(self):
        """连接服务器"""
        self.show_header("学生管理系统")
        self.console.print("正在连接服务器...", style="yellow")

        if self.network.connect():
            return True
        else:
            self.console.print(
                "❌ 无法连接服务器，请检查网络或服务器状态", style="bold red"
            )
            return False

    def login_screen(self):
        """登录界面"""
        while True:
            self.show_header("用户登录")

            username = Prompt.ask("请输入用户名")
            password = Prompt.ask("请输入密码", password=True)

            success, message, permission = self.auth.login(username, password)

            if success:
                self.current_user = username
                self.permission = permission
                self.console.print(f"✅ {message}", style="bold green")
                time.sleep(1)
                return True
            else:
                self.console.print(f"❌ {message}", style="bold red")

                if not Confirm.ask("是否重试"):
                    return False

    def main_menu(self):
        """主菜单"""
        while True:
            self.show_header(f"主菜单 [用户: {self.current_user} ({self.permission})]")

            options = [
                "1. 查询所有学生成绩",
                "2. 按学号查询成绩",
                "3. 查看成绩统计",
                "4. 修改密码",
            ]

            if self.permission == "admin":
                options.append("5. 学生管理")
                options.append("6. 账户管理")

            options.append("0. 退出系统")

            # 显示选项
            for option in options:
                self.console.print(option)

            choice = Prompt.ask(
                "请选择操作", choices=[str(i) for i in range(len(options))]
            )

            if choice == "0":
                return False
            elif choice == "1":
                self.query_all_students()
            elif choice == "2":
                self.query_student_by_id()
            elif choice == "3":
                self.show_statistic()
            elif choice == "4":
                self.change_password()
            elif choice == "5" and self.permission == "admin":
                self.student_management_menu()
            elif choice == "6" and self.permission == "admin":
                self.account_management_menu()

    def query_all_students(self):
        """查询所有学生"""

        self.show_header("所有学生成绩")

        success, data = self.student_manager.query_all_students()

        if not success:
            self.console.print(f"❌ {data}", style="bold red")
            time.sleep(2)
            return

        if not data:
            self.console.print("没有学生数据", style="yellow")
            time.sleep(2)
            return

        # 创建表格显示学生数据
        table = Table(title="学生成绩列表", box=box.ROUNDED)
        table.add_column("学号", style="cyan")
        table.add_column("姓名", style="magenta")
        table.add_column("性别")
        table.add_column("科目1", justify="right")
        table.add_column("科目2", justify="right")
        table.add_column("科目3", justify="right")
        table.add_column("总分", justify="right", style="bold")

        for student in data:
            if isinstance(student, dict):
                table.add_row(
                    student["student_id"],
                    student["name"],
                    student["gender"],
                    f"{student['score1']:.1f}",
                    f"{student['score2']:.1f}",
                    f"{student['score3']:.1f}",
                    f"{student['total']:.1f}",
                )
            else:
                print(f"学生格式不是字典: {type(student)}")

        self.console.print(table)
        Prompt.ask("按回车键返回主菜单")

    def query_student_by_id(self):
        """按学号查询学生"""
        self.show_header("按学号查询")

        student_id = Prompt.ask("请输入学号")
        success, data = self.student_manager.query_student_by_id(student_id)

        if not success:
            self.console.print(f"❌ {data}", style="bold red")
            time.sleep(2)
            return

        # 显示学生详情
        self.show_header(f"学生详情 - {student_id}")
        table = Table(box=box.SIMPLE)
        table.add_column("属性", style="cyan")
        table.add_column("值", style="magenta")

        if isinstance(data, dict):
            table.add_row("学号", data["student_id"])
            table.add_row("姓名", data["name"])
            table.add_row("性别", data["gender"])
            table.add_row("科目1成绩", f"{data['score1']:.1f}")
            table.add_row("科目2成绩", f"{data['score2']:.1f}")
            table.add_row("科目3成绩", f"{data['score3']:.1f}")
            table.add_row("总分", f"{data['total']:.1f}")

        self.console.print(table)
        Prompt.ask("按回车键返回主菜单")

    def show_statistic(self):
        """显示成绩统计"""
        self.show_header("成绩统计")

        success, data = self.student_manager.get_statistics()

        if not success:
            self.console.print(f"❌ {data}", style="bold red")
            time.sleep(2)
            return

        table = Table(title="各科成绩统计", box=box.ROUNDED)
        table.add_column("科目", style="cyan")
        table.add_column("平均分", style="green")
        table.add_column("最高分", style="yellow")

        if isinstance(data, dict):
            for subject, scores in data.items():
                # 安全处理整数和浮点数
                try:
                    avg_value = float(scores["avg"])
                    max_value = float(scores["max"])
                except (TypeError, ValueError):
                    avg_value = 0.0
                    max_value = 0.0

                table.add_row(subject, f"{avg_value:.1f}", f"{max_value:.1f}")

        self.console.print(table)
        Prompt.ask("按回车键返回主菜单")

    def change_password(self):
        """修改密码"""
        self.show_header("修改密码")

        old_password = Prompt.ask("请输入当前密码", password=True)
        new_password = Prompt.ask("请输入新密码", password=True)
        confirm_password = Prompt.ask("请确认新密码", password=True)

        if new_password != confirm_password:
            self.console.print("❌ 两次输入的新密码不一致", style="bold red")
            time.sleep(2)
            return

        success, message = self.auth.change_password(old_password, new_password)

        if success:
            self.console.print(f"✅ {message}", style="bold green")
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def student_management_menu(self):
        """学生管理菜单（管理员）"""
        while True:
            self.show_header("学生管理")

            options = ["1. 添加学生", "2. 更新学生信息", "3. 删除学生", "0. 返回主菜单"]

            for option in options:
                self.console.print(option)

            choice = Prompt.ask("请选择操作", choices=["0", "1", "2", "3"])

            if choice == "0":
                return
            elif choice == "1":
                self.add_student()
            elif choice == "2":
                self.update_student()
            elif choice == "3":
                self.delete_student()

    def add_student(self):
        """添加学生（管理员）"""
        self.console.print("添加学生")

        student_data = {}

        student_data["student_id"] = Prompt.ask("请输入学号")
        student_data["name"] = Prompt.ask("请输入姓名")
        student_data["gender"] = Prompt.ask("请输入性别（男/女）", choices=["男", "女"])
        student_data["score1"] = Prompt.ask("请输入科目1成绩")
        student_data["score2"] = Prompt.ask("请输入科目2成绩")
        student_data["score3"] = Prompt.ask("请输入科目3成绩")

        success, message = self.admin_student_manager.add_student(student_data)

        if success:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def update_student(self):
        """更新学生信息（管理员）"""
        self.console.print("更新学生信息")

        student_id = Prompt.ask("请输入要更新的学生学号")

        # 先查询学生信息
        success, student_data = self.student_manager.query_student_by_id(student_id)

        if not success:
            self.console.print(f"❌ 学生{student_id}不存在", style="bold red")
            time.sleep(2)
            return

        # 显示当前信息
        if isinstance(student_data, dict):
            self.console.print(f"当前学生信息: {student_data['name']} ({student_id})")

            # 获取更新信息
            student_data["name"] = Prompt.ask(
                "请输入新姓名", default=student_data["name"]
            )
            student_data["gender"] = Prompt.ask(
                "请输入新性别（男/女）",
                choices=["男", "女"],
                default=student_data["gender"],
            )
            student_data["score1"] = float(
                Prompt.ask("请输入新科目1成绩", default=str(student_data["score1"]))
            )
            student_data["score2"] = float(
                Prompt.ask("请输入新科目2成绩", default=str(student_data["score2"]))
            )
            student_data["score3"] = float(
                Prompt.ask("请输入新科目3成绩", default=str(student_data["score3"]))
            )
        else:
            self.console.print(f"❌ 学生格式错误，返回的不是dict: {type(student_data)}")

        # 发送更新请求
        success, message = self.admin_student_manager.update_student(student_data)

        if success:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def delete_student(self):
        """删除学生（管理员）"""
        self.show_header("删除学生")

        student_id = Prompt.ask("请输入要删除的学生学号")

        if not Confirm.ask(f"确定要删除学生 {student_id} 吗?"):
            return

        success, message = self.admin_student_manager.delete_student(student_id)

        if success:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def account_management_menu(self):
        """账户管理菜单（管理员）"""
        while True:
            self.show_header("账户管理")

            options = [
                "1. 查看账户列表",
                "2. 修改账户权限",
                "3. 删除账户",
                "0. 返回主菜单",
            ]

            for option in options:
                self.console.print(option)

            choice = Prompt.ask("请选择操作", choices=["0", "1", "2", "3"])

            if choice == "0":
                return
            elif choice == "1":
                self.list_accounts()
            elif choice == "2":
                self.update_permission()
            elif choice == "3":
                self.delete_account()

    def list_accounts(self):
        """查看账户列表（管理员）"""
        self.show_header("账户列表")

        success, accounts = self.admin_account_manager.list_accounts()

        if not success:
            self.console.print(f"❌ {accounts}", style="bold red")
            time.sleep(2)
            return

        if not accounts:
            self.console.print("没有账户数据", style="yellow")
            time.sleep(2)
            return

        table = Table(title="系统账户", box=box.ROUNDED)
        table.add_column("用户名", style="cyan")
        table.add_column("权限", style="magenta")
        table.add_column("创建时间")

        for account in accounts:
            if isinstance(account, dict):
                table.add_row(
                    account["username"], account["permission"], account["created_at"]
                )

        self.console.print(table)
        Prompt.ask("按回车键返回")

    def update_permission(self):
        """修改账户权限（管理员）"""
        self.show_header("修改账户权限")

        username = Prompt.ask("请输入用户名")
        new_permission = Prompt.ask(
            "请输入新权限（admin/user）", choices=["admin", "user"]
        )

        success, message = self.admin_account_manager.update_permission(
            username, new_permission
        )

        if success:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def delete_account(self):
        """删除账户（管理员）"""
        self.show_header("删除账户")

        username = Prompt.ask("请输入要删除的用户名")

        if username == self.current_user:
            self.console.print("❌ 不能删除当前登录账户", style="bold red")
            time.sleep(2)
            return

        if not Confirm.ask(f"确定要删除账户 {username} 吗?"):
            return

        success, message = self.admin_account_manager.delete_account(username)

        if success:
            self.console.print(f"✅ {message}", style="bold green")
        else:
            self.console.print(f"❌ {message}", style="bold red")

        time.sleep(2)

    def logout(self):
        """注销用户"""
        self.auth.logout()
        self.current_user = None
        self.permission = None
        self.console.print("✅ 已成功注销", style="bold green")
        time.sleep(1)

    def run(self):
        """运行CLI应用"""
        try:
            if not self.connect_to_server():
                return

            while True:
                if not self.login_screen():
                    break

                if self.main_menu() is False:
                    break

                self.logout()

            self.network.close()
            self.console.print("👋 感谢使用学生成绩管理系统", style="bold blue")
        except KeyboardInterrupt:
            self.network.close()
            self.console.print("\n👋 程序已退出", style="bold blue")
        except Exception as e:
            self.logger.error(f"运行时错误: {str(e)}")
            self.console.print(f"❌ 系统错误: {str(e)}", style="bold red")
            self.network.close()


# 启动脚本
if __name__ == "__main__":
    cli = StudentManagementCLI()
    cli.run()
