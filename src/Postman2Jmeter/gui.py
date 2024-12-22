import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QRadioButton, QPushButton, 
                           QFileDialog, QLabel, QButtonGroup, QLineEdit,
                           QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from .converter import convert_to_jmx

class TestPlanDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置TestPlan")
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        # TestPlan名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("请输入TestPlan名称")
        layout.addWidget(QLabel("TestPlan名称:"))
        layout.addWidget(self.name_input)
        
        # 确定取消按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Postman/ApiPost导出JSON文件转JMeter用例")
        self.setMinimumSize(800, 500)
        
        # 初始化输入框
        self.collection_path = QLineEdit()
        self.env_path = QLineEdit()
        self.apipost_path = QLineEdit()
        self.output_path = QLineEdit()
        
        # ��窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("Postman/ApiPost导出JSON文件转JMeter用例")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 注意事项区域
        tips_widget = QWidget()
        tips_widget.setStyleSheet("""
            QWidget {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #856404;
                font-size: 12px;
                background: transparent;
                padding: 2px 0;
            }
        """)
        tips_layout = QVBoxLayout(tips_widget)
        tips_layout.setSpacing(2)
        tips_layout.setContentsMargins(10, 5, 10, 5)
        
        tips_title = QLabel("注意事项：")
        tips_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        tips_layout.addWidget(tips_title)
        
        tips = [
            "1. Postman格式：请使用 Collection v2.1 版本导出的 JSON 文件",
            "2. ApiPost格式：请使用 ApiPost 导出的 JSON 文件",
            "3. 输出路径默认与输入文件在同一目录",
            "4. 生成的 JMX 文件可直接导入 JMeter 使用",
            "5. 支持文件夹嵌套结构，将自动转换为 ThreadGroup"
        ]
        
        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setWordWrap(True)
            tips_layout.addWidget(tip_label)
        
        layout.addWidget(tips_widget)
        
        # 模式选择区域
        mode_widget = QWidget()
        mode_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 10px;
            }
            QRadioButton {
                font-size: 13px;
                padding: 5px 15px;
            }
            QRadioButton:hover {
                background-color: #e9ecef;
                border-radius: 4px;
            }
        """)
        mode_layout = QHBoxLayout(mode_widget)
        mode_layout.setSpacing(20)
        mode_layout.setContentsMargins(10, 5, 10, 5)
        
        mode_group = QButtonGroup(self)
        self.postman_radio = QRadioButton("Postman")
        self.apipost_radio = QRadioButton("ApiPost")
        mode_group.addButton(self.postman_radio)
        mode_group.addButton(self.apipost_radio)
        mode_layout.addWidget(self.postman_radio)
        mode_layout.addWidget(self.apipost_radio)
        mode_layout.addStretch()
        
        layout.addWidget(mode_widget)
        
        # 模式选择区域通用样式
        self.file_widget_style = """
            QWidget {
                background-color: #f8f9fa;
                border-radius: 6px;
                padding: 5px;
            }
            QLabel {
                background: transparent;
                font-size: 13px;
                color: #495057;
                padding: 0 5px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                min-height: 20px;
            }
            QPushButton {
                padding: 5px 10px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """
        
        # Postman区域
        self.postman_widget = self.create_file_section([
            ("Collection文件:", self.collection_path, "请选择Postman Collection文件"),
            ("Environment文件 (可选):", self.env_path, "请选择Postman Environment文件")
        ])
        layout.addWidget(self.postman_widget)
        
        # ApiPost区域
        self.apipost_widget = self.create_file_section([
            ("ApiPost文件:", self.apipost_path, "请选择ApiPost导出的JSON文件")
        ])
        layout.addWidget(self.apipost_widget)
        
        # 输出路径区域
        self.output_widget = self.create_file_section([
            ("输出路径:", self.output_path, "输出路径（与输入文件同级目录）")
        ])
        layout.addWidget(self.output_widget)
        
        # 转换按钮
        convert_btn = QPushButton("开始转换")
        convert_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(convert_btn)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
                padding: 10px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 信号连接
        self.postman_radio.toggled.connect(self.toggle_mode)
        self.apipost_radio.toggled.connect(self.toggle_mode)
        collection_btn = self.postman_widget.findChild(QPushButton)
        if collection_btn:
            collection_btn.clicked.connect(lambda: self.select_file(self.collection_path, "Postman Collection (*.json)"))
        env_btn = self.postman_widget.findChildren(QPushButton)[1]
        if env_btn:
            env_btn.clicked.connect(lambda: self.select_file(self.env_path, "Postman Environment (*.json)"))
        apipost_btn = self.apipost_widget.findChild(QPushButton)
        if apipost_btn:
            apipost_btn.clicked.connect(lambda: self.select_file(self.apipost_path, "ApiPost Export (*.json)"))
        output_btn = self.output_widget.findChild(QPushButton)
        if output_btn:
            output_btn.clicked.connect(self.select_output_dir)
        convert_btn.clicked.connect(self.convert)
        
        # 初始化界面
        self.postman_radio.setChecked(True)
        self.toggle_mode()

    def create_file_section(self, fields):
        """创建文件选择区域"""
        widget = QWidget()
        widget.setStyleSheet(self.file_widget_style)
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)  # 减小边距
        
        for label_text, line_edit, placeholder in fields:
            field_layout = QHBoxLayout()  # 改为水平布局
            field_layout.setSpacing(10)
            
            label = QLabel(label_text)
            label.setFixedWidth(120)  # 固定标签宽度
            
            line_edit.setPlaceholderText(placeholder)
            btn = QPushButton("选择文件" if "路径" not in label_text else "选择路径")
            btn.setFixedWidth(80)  # 固定按钮宽度
            
            field_layout.addWidget(label)
            field_layout.addWidget(line_edit, 1)  # 设置拉伸因子为1，使输入框自动填充剩余空间
            field_layout.addWidget(btn)
            
            layout.addLayout(field_layout)
        
        return widget

    def toggle_mode(self):
        is_postman = self.postman_radio.isChecked()
        self.postman_widget.setVisible(is_postman)
        self.apipost_widget.setVisible(not is_postman)
        
        # 清空输入框内容
        if is_postman:
            # 切换到 Postman 模式时清空 ApiPost 输入框
            self.apipost_path.clear()
        else:
            # 切换到 ApiPost 模式时清空 Postman 输入框
            self.collection_path.clear()
            self.env_path.clear()
        
        # 清空输出路径
        self.output_path.clear()
        
        # 清空状态标签
        self.status_label.clear()
        
    def select_file(self, line_edit, file_filter):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            file_filter
        )
        if file_name:
            line_edit.setText(file_name)
            # 只有当输出路径为空时才自动设置
            if not self.output_path.text():
                self.output_path.setText(os.path.dirname(file_name))
            
    def select_output_dir(self):
        dir_name = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_path.text() or ""  # 如果当前有路径使用当前路径为起始目录
        )
        if dir_name:
            self.output_path.setText(dir_name)
        
    def validate_inputs(self):
        if self.postman_radio.isChecked():
            if not self.collection_path.text():
                QMessageBox.warning(self, "警告", "请选择Postman Collection文件！")
                return False
        else:
            if not self.apipost_path.text():
                QMessageBox.warning(self, "警告", "请选择ApiPost导出文件！")
                return False
        return True
            
    def convert(self):
        if not self.validate_inputs():
            return
            
        # 获取TestPlan名称
        dialog = TestPlanDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        test_plan_name = dialog.name_input.text()
        if not test_plan_name:
            QMessageBox.warning(self, "警告", "TestPlan名称不能为空！")
            return
            
        try:
            self.status_label.setText("正在转换...")
            self.status_label.repaint()
            
            # 使用输出路径
            output_dir = self.output_path.text()
            
            # 执行转换
            if self.postman_radio.isChecked():
                output_file = convert_to_jmx(
                    'postman',
                    self.collection_path.text(),
                    self.env_path.text() if self.env_path.text() else None,
                    test_plan_name,
                    output_dir
                )
            else:
                output_file = convert_to_jmx(
                    'apipost',
                    self.apipost_path.text(),
                    None,
                    test_plan_name,
                    output_dir
                )
                
            self.status_label.setText("转换完成！")
            QMessageBox.information(
                self, 
                "成功", 
                f"转换完成！\n文件已保存至：{output_file}"
            )
        except Exception as e:
            self.status_label.setText("转换失败！")
            QMessageBox.critical(self, "错误", f"转换失败：{str(e)}")
