import sys
import sqlite3
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QFormLayout,
    QTextEdit,
)


class QuizDatabase:
    def __init__(self):
        self.connection = sqlite3.connect("quiz.db")
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            score INTEGER NOT NULL,
            type TEXT NOT NULL,
            point TEXT NOT NULL,
            course TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            answer TEXT NOT NULL,
            selected_last_three_years BOOLEAN NOT NULL
        )"""
        )
        self.connection.commit()

    def add_question(self, question):
        self.cursor.execute(
            """
        INSERT INTO questions (content, score, type, point, course, difficulty, answer, selected_last_three_years)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            question,
        )
        self.connection.commit()

    def delete_question(self, question_id):
        self.cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self.connection.commit()

    def update_question(self, question_id, question):
        self.cursor.execute(
            """
        UPDATE questions SET content = ?, score = ?, type = ?, point = ?, course = ?, difficulty = ?, answer = ?, selected_last_three_years = ?
        WHERE id = ?""",
            (*question, question_id),
        )
        self.connection.commit()

    def get_questions(self):
        self.cursor.execute("SELECT * FROM questions")
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()


class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = QuizDatabase()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("题库系统")

        layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # 新增题目标签
        self.add_tab = QWidget()
        self.add_layout = QFormLayout()

        self.content_input = QTextEdit(self)
        self.score_input = QLineEdit(self)
        self.type_input = QLineEdit(self)
        self.point_input = QLineEdit(self)
        self.course_input = QLineEdit(self)
        self.difficulty_input = QLineEdit(self)
        self.answer_input = QTextEdit(self)
        self.selected_input = QLineEdit(self)

        self.add_layout.addRow("考题内容:", self.content_input)
        self.add_layout.addRow("分数:", self.score_input)
        self.add_layout.addRow("题目类型:", self.type_input)
        self.add_layout.addRow("考点:", self.point_input)
        self.add_layout.addRow("所属课程:", self.course_input)
        self.add_layout.addRow("难度:", self.difficulty_input)
        self.add_layout.addRow("答案:", self.answer_input)
        self.add_layout.addRow("近三年是否被选中 (1为是, 0为否):", self.selected_input)

        add_button = QPushButton("新增题目", self)
        add_button.clicked.connect(self.add_question)
        self.add_layout.addWidget(add_button)
        self.add_tab.setLayout(self.add_layout)
        self.tab_widget.addTab(self.add_tab, "新增题目")

        # 查询题目标签
        self.query_tab = QWidget()
        self.query_layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(
            [
                "ID",
                "考题内容",
                "分数",
                "类型",
                "考点",
                "课程",
                "难度",
                "答案",
                "近三年选中",
            ]
        )
        self.query_layout.addWidget(self.table)
        self.load_questions()
        self.query_tab.setLayout(self.query_layout)
        self.tab_widget.addTab(self.query_tab, "查询题目")

        # 修改题目标签
        self.update_tab = QWidget()
        self.update_layout = QFormLayout()

        self.update_content_input = QTextEdit(self)
        self.update_score_input = QLineEdit(self)
        self.update_type_input = QLineEdit(self)
        self.update_point_input = QLineEdit(self)
        self.update_course_input = QLineEdit(self)
        self.update_difficulty_input = QLineEdit(self)
        self.update_answer_input = QTextEdit(self)
        self.update_selected_input = QLineEdit(self)

        self.update_layout.addRow("考题内容:", self.update_content_input)
        self.update_layout.addRow("分数:", self.update_score_input)
        self.update_layout.addRow("题目类型:", self.update_type_input)
        self.update_layout.addRow("考点:", self.update_point_input)
        self.update_layout.addRow("所属课程:", self.update_course_input)
        self.update_layout.addRow("难度:", self.update_difficulty_input)
        self.update_layout.addRow("答案:", self.update_answer_input)
        self.update_layout.addRow(
            "近三年是否被选中 (1为是, 0为否):", self.update_selected_input
        )

        update_button = QPushButton("更改题目", self)
        update_button.clicked.connect(self.update_question)
        self.update_layout.addWidget(update_button)

        self.update_tab.setLayout(self.update_layout)
        self.tab_widget.addTab(self.update_tab, "修改题目")

        # 删除题目标签
        self.delete_tab = QWidget()
        self.delete_layout = QVBoxLayout()
        delete_button = QPushButton("删除题目", self)
        delete_button.clicked.connect(self.delete_question)
        self.delete_layout.addWidget(delete_button)
        self.delete_tab.setLayout(self.delete_layout)
        self.tab_widget.addTab(self.delete_tab, "删除题目")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

        # 连接查询表格的双击事件
        self.table.cellDoubleClicked.connect(self.load_selected_question)

    def load_questions(self):
        self.table.setRowCount(0)
        questions = self.db.get_questions()
        for question in questions:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for col, data in enumerate(question):
                self.table.setItem(row_position, col, QTableWidgetItem(str(data)))

    def load_selected_question(self, row, column):
        question_data = [
            self.table.item(row, i).text() for i in range(self.table.columnCount())
        ]
        self.update_content_input.setText(question_data[1])
        self.update_score_input.setText(question_data[2])
        self.update_type_input.setText(question_data[3])
        self.update_point_input.setText(question_data[4])
        self.update_course_input.setText(question_data[5])
        self.update_difficulty_input.setText(question_data[6])
        self.update_answer_input.setText(question_data[7])
        self.update_selected_input.setText(question_data[8])

    def add_question(self):
        try:
            question = (
                self.content_input.toPlainText(),
                int(self.score_input.text()),
                self.type_input.text(),
                self.point_input.text(),
                self.course_input.text(),
                self.difficulty_input.text(),
                self.answer_input.toPlainText(),
                bool(int(self.selected_input.text())),
            )
            self.db.add_question(question)
            self.load_questions()
            QMessageBox.information(self, "成功", "题目已成功添加")
            self.clear_add_fields()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def clear_add_fields(self):
        self.content_input.clear()
        self.score_input.clear()
        self.type_input.clear()
        self.point_input.clear()
        self.course_input.clear()
        self.difficulty_input.clear()
        self.answer_input.clear()
        self.selected_input.clear()

    def update_question(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请选择要更改的题目")
            return

        question_id = int(self.table.item(selected_row, 0).text())
        try:
            question = (
                self.update_content_input.toPlainText(),
                int(self.update_score_input.text()),
                self.update_type_input.text(),
                self.update_point_input.text(),
                self.update_course_input.text(),
                self.update_difficulty_input.text(),
                self.update_answer_input.toPlainText(),
                bool(int(self.update_selected_input.text())),
            )
            self.db.update_question(question_id, question)
            self.load_questions()
            QMessageBox.information(self, "成功", "题目已成功更改")
            self.clear_update_fields()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def clear_update_fields(self):
        self.update_content_input.clear()
        self.update_score_input.clear()
        self.update_type_input.clear()
        self.update_point_input.clear()
        self.update_course_input.clear()
        self.update_difficulty_input.clear()
        self.update_answer_input.clear()
        self.update_selected_input.clear()

    def delete_question(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的题目")
            return

        question_id = int(self.table.item(selected_row, 0).text())
        self.db.delete_question(question_id)
        self.load_questions()
        QMessageBox.information(self, "成功", "题目已成功删除")

    def closeEvent(self, event):
        self.db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuizApp()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
