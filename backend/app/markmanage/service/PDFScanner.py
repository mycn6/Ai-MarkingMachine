import os
import time

import twain
from PIL import Image
from io import BytesIO
import argparse
import sys
from datetime import datetime


class PDFScanner:
    def __init__(self, scanner_name=None, scan_dir="scans", resolution=300, source="ADF", timeout=30):
        """
        初始化PDF扫描仪对象

        :param scanner_name: 扫描仪设备名称，如果为None则使用默认扫描仪
        :param scan_dir: 扫描文件保存目录
        :param resolution: 扫描分辨率 (DPI)
        :param source: 扫描来源 (ADF|Flatbed)
        :param timeout: 扫描超时时间（秒）
        """
        # 设置扫描目录
        self.scan_dir = scan_dir
        os.makedirs(self.scan_dir, exist_ok=True)

        self.scanner_name = scanner_name
        self.resolution = resolution
        self.source = source.upper()
        self.timeout = timeout
        self.src = None  # TWAIN 扫描源对象
        self.sm = None  # TWAIN SourceManager 对象
        self.all_pdfs = []  # 存储所有生成的PDF路径

        # 验证参数有效性
        self._validate_parameters()

        # 连接扫描仪设备
        self._connect_to_scanner()

    def _validate_parameters(self):
        """验证初始化参数的有效性"""
        # 验证分辨率
        if self.resolution < 75 or self.resolution > 1200:
            raise ValueError(f"无效的分辨率值: {self.resolution}. 应在75-1200之间")

        # 验证来源
        valid_sources = ["ADF", "FLATBED"]
        if self.source not in valid_sources:
            raise ValueError(f"无效的扫描来源: {self.source}. 应为ADF或Flatbed")

    def _connect_to_scanner(self):
        """连接到指定名称的扫描仪设备"""
        try:

            # 初始化TWAIN环境
            self.sm = twain.SourceManager(0)
            available_scanners = self.get_available_scanners()

            if not available_scanners:
                raise RuntimeError("未检测到连接的扫描设备")

            # 寻找匹配设备名称的扫描仪
            selected_scanner = None
            for scanner_info in available_scanners:
                # 如果未指定设备名称，使用第一个设备
                if self.scanner_name is None:
                    selected_scanner = scanner_info['name']
                    break

                # 检查设备名称是否匹配（支持部分匹配）
                if self.scanner_name.lower() in scanner_info['name'].lower():
                    selected_scanner = scanner_info['name']
                    break

            if not selected_scanner:
                scanners_str = ", ".join([s['name'] for s in available_scanners])
                raise RuntimeError(f"未找到扫描仪: {self.scanner_name}。可用设备: {scanners_str}")

            # 打开选择的扫描仪
            self.src = self.sm.OpenSource(selected_scanner)
            print(f"✅ 已连接到扫描仪: {selected_scanner}")

        except Exception as e:
            raise RuntimeError(f"扫描仪连接失败,具体错误信息:{str(e)}")

    def get_available_scanners(self):
        """获取所有可用扫描仪列表"""
        scanners = []
        if not self.sm:
            # 如果SourceManager未初始化，临时创建一个
            try:
                temp_sm = twain.SourceManager(0)
                scanner_names = temp_sm.GetSourceList()
                scanners = [{"name": name} for name in scanner_names]
            except:
                pass
            return scanners

        # 使用已初始化的SourceManager
        return [{"name": name} for name in self.sm.GetSourceList()]

    def scan(self, file_name=None):
        """
        执行扫描任务并生成PDF文件

        :param file_name: 基础文件名（可选）
        :return: bool 扫描是否成功
        """
        try:
            # 设置扫描参数
            self._setup_scanner()

            # 用户确认提示
            self._show_scan_prompt()

            # 执行扫描流程
            return self._scan_documents(file_name)

        except Exception as e:
            print(f"扫描失败: {str(e)}")
            return False
        finally:
            self._cleanup_resources()

    def _setup_scanner(self):
        """配置扫描仪参数"""
        # 设置基本参数
        self.src.SetCapability(twain.ICAP_XRESOLUTION, twain.TWTY_UINT16, self.resolution)
        self.src.SetCapability(twain.ICAP_YRESOLUTION, twain.TWTY_UINT16, self.resolution)
        self.src.SetCapability(twain.ICAP_PIXELTYPE, twain.TWTY_UINT16, twain.TWPT_RGB)

        # 设置ADF或平板模式
        if self._is_adf():
            print("启用自动进纸器 (ADF)")
            self.src.SetCapability(twain.CAP_FEEDERENABLED, twain.TWTY_BOOL, True)
            self.src.SetCapability(twain.CAP_AUTOFEED, twain.TWTY_BOOL, True)
        else:
            print("使用平板扫描模式")

        print(f"扫描参数设置完成 (分辨率: {self.resolution} DPI, 来源: {self.source})")

    def _is_adf(self):
        """检查是否使用ADF模式"""
        return self.source == "ADF"

    def _show_scan_prompt(self):
        """显示用户准备提示"""
        if self._is_adf():
            input("请将文档放入ADF进纸器，按Enter开始扫描...")
        else:
            input("请将文档放在平板上，按Enter开始扫描...")

    def _scan_documents(self, filename):
        """执行扫描文档主流程"""
        print("开始扫描...")
        self.src.RequestAcquire(show_ui=False, modal_ui=False)
        page_count = 0
        sheet_count = 0
        current_sheet_images = []
        scan_complete = False
        start_time = time.time()

        try:
            while not scan_complete and (time.time() - start_time < self.timeout):
                try:
                    (handle, remaining_count) = self.src.XferImageNatively()
                    page_count, current_sheet_images = self._process_image(
                        handle, page_count, current_sheet_images
                    )

                    # 处理纸张分割逻辑
                    if not self._is_adf() or remaining_count <= 0:
                        sheet_count = self._finalize_sheet(
                            current_sheet_images, filename, sheet_count
                        )
                        current_sheet_images = []
                        scan_complete = self._is_adf() and (remaining_count <= 0)

                except Exception as e:
                    scan_complete = self._handle_scan_error(e, current_sheet_images, filename, sheet_count)
                    # if scan_complete:
                    break

            return self._finalize_scan(scan_complete, current_sheet_images, filename, sheet_count)

        except KeyboardInterrupt:
            return self._handle_keyboard_interrupt(current_sheet_images, filename, sheet_count)

    def _process_image(self, handle, page_count, current_sheet_images):
        """处理获取到的扫描图像"""
        try:
            bmp_bytes = twain.DIBToBMFile(handle)
            img = Image.open(BytesIO(bmp_bytes)).convert("RGB")
            page_count += 1
            print(f"已扫描第 {page_count} 页，尺寸: {img.size}")
            current_sheet_images.append(img)
            self._close_image_handle(handle)
        except Exception as e:
            print(f"图像处理失败: {str(e)}")
            self._close_image_handle(handle)
            raise
        return page_count, current_sheet_images

    def _close_image_handle(self, handle):
        """安全关闭图像句柄"""
        try:
            if handle and self.src:
                self.src.CloseImageFile(handle)
        except:
            pass

    def _finalize_sheet(self, images, filename, sheet_count):
        """完成当前纸张的保存"""
        if images:
            sheet_count += 1
            pdf_path = self._save_sheet_as_pdf(images, filename, sheet_count)
            self.all_pdfs.append(pdf_path)
            # print(f"已保存第 {sheet_count} 张纸的PDF: {os.path.basename(pdf_path)}")
            print(f"已保存所有纸张的扫描结果为一个PDF: {os.path.basename(pdf_path)}")
        return sheet_count

    def _handle_scan_error(self, e, current_sheet_images, filename, sheet_count):
        """处理扫描错误"""
        if "No more images" in str(e):
            if current_sheet_images:
                sheet_count = self._finalize_sheet(current_sheet_images, filename, sheet_count)
            print("所有页面扫描完成")
            return True  # 标记扫描完成
        elif "操作已取消" in str(e):
            print("扫描操作被取消")
            return True
        else:
            print(f"扫描错误")
            time.sleep(1)
            return False

    def _finalize_scan(self, scan_complete, current_sheet_images, filename, sheet_count):
        """最终处理扫描结果"""
        if not scan_complete:
            print(f"扫描超时 ({self.timeout} 秒)")
            if current_sheet_images:
                sheet_count = self._finalize_sheet(current_sheet_images, filename, sheet_count)

        if not self.all_pdfs:
            print("未生成任何PDF文件")
            return False

        print(f"成功生成 {len(self.all_pdfs)} 个PDF文件")
        for pdf in self.all_pdfs:
            print(f"- {pdf}")
        return True

    def _handle_keyboard_interrupt(self, current_sheet_images, filename, sheet_count):
        """处理用户中断"""
        print("\n用户通过Ctrl+C终止扫描")
        if current_sheet_images:
            sheet_count = self._finalize_sheet(current_sheet_images, filename, sheet_count)
        return len(self.all_pdfs) > 0

    def _save_sheet_as_pdf(self, images, base_filename, sheet_number):
        """保存所有扫描的纸张为一个PDF"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = base_filename or f"scan_{timestamp}"
            pdf_name = f"{base_name}_sheet{sheet_number}.pdf"
            output_path = os.path.join(self.scan_dir, pdf_name)

            # 确保PDF名称唯一
            counter = 1
            while os.path.exists(output_path):
                pdf_name = f"{base_name}_sheet{sheet_number}_{counter}.pdf"
                output_path = os.path.join(self.scan_dir, pdf_name)
                counter += 1

            images[0].save(
                output_path,
                "PDF",
                resolution=self.resolution,
                save_all=True,
                append_images=images[1:],
                quality=100,
                subsampling=0
            )
            return output_path
        except Exception as e:
            print(f"保存第 {sheet_number} 张纸的PDF失败: {str(e)}")
            return None

    def _cleanup_resources(self):
        """安全清理资源"""
        try:
            if self.src:
                self.src = None
            if self.sm:
                self.sm = None
        except Exception as e:
            print(f"⚠️ 关闭扫描源失败: {str(e)}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="PDF扫描工具")
    parser.add_argument("-d", "--dir", default="scans", help="扫描文件保存目录")
    parser.add_argument("-r", "--res", type=int, default=300,
                        choices=range(75, 1201), metavar="[75-1200]",
                        help="扫描分辨率 (DPI)")
    parser.add_argument("-s", "--source", choices=["ADF", "Flatbed"], default="ADF",
                        help="扫描来源")
    parser.add_argument("-f", "--file", help="指定基础PDF文件名")
    parser.add_argument("--timeout", type=int, default=60, help="扫描超时时间（秒）")
    parser.add_argument("--scanner", default="ES-580W", help="指定扫描仪设备名称")
    return parser.parse_args()


def main():
    """主程序逻辑"""
    args = parse_arguments()

    try:
        # 初始化扫描仪
        scanner = PDFScanner(
            scanner_name=args.scanner,
            scan_dir=args.dir,
            source=args.source,
            timeout=args.timeout,
            resolution=args.res  # 需确保PDFScanner支持此参数
        )

        # 显示可用扫描仪列表
        print("🖨️ 可用扫描仪列表:")
        for i, scanner_info in enumerate(scanner.get_available_scanners(), 1):
            print(f"{i}. {scanner_info['name']}")

        # 执行扫描
        success = scanner.scan(file_name=args.file)
        return 0 if success else 1

    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
