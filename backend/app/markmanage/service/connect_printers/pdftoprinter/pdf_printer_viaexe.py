import subprocess
import os


class Printer:
    def __init__(self, exe_path, printer_name):
        """
        初始化 PDF 打印器

        :param exe_path: PDFtoPrinter.exe 的完整路径
        :param printer_name: 打印机名称（如控制面板中显示的）
        """
        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"PDFtoPrinter.exe 未找到: {exe_path}")
        self.exe_path = exe_path
        self.printer_name = printer_name

    def print(self, pdf_path):
        """
        打印 PDF 文件（默认双面）

        :param pdf_path: 要打印的 PDF 文件路径
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 文件未找到: {pdf_path}")

        # 始终启用双面默认设置
        command = [self.exe_path, pdf_path, self.printer_name]

        print(f"🖨️ 正在发送双面打印任务: {pdf_path}")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 打印命令发送成功。")
        else:
            print("❌ 打印失败：")
            print(result.stderr)


# 示例用法
if __name__ == "__main__":
    exe_path = r"../tools/PDFtoPrinter.exe"  # 替换为你自己的路径
    printer_name = "HUAWEI CV81-WDMSE-0565-ipv4"
    pdf_file_path = r"../pdf_files/test.pdf"


    printer = Printer(exe_path, printer_name)
    printer.print(pdf_file_path)  # 无需设置双面，自动启用
