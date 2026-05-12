import unittest
import tkinter as tk

from app.gui.log_panel import StdoutRedirector, LogPanel, BaseLayout


class TestStdoutRedirector(unittest.TestCase):

    def test_TC_G01_01_write_captures_text(self):
        """write() 호출 시 콜백에 텍스트가 전달된다."""
        captured = []
        r = StdoutRedirector(captured.append)
        r.write("hello\n")
        self.assertEqual(captured, ["hello\n"])

    def test_TC_G01_02_write_accumulates(self):
        """여러 번 write() 시 콜백이 순서대로 호출된다."""
        captured = []
        r = StdoutRedirector(captured.append)
        r.write("a")
        r.write("b")
        self.assertEqual(''.join(captured), "ab")


class TestLogPanel(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()          # 화면 표시 없이 테스트
        self.panel = LogPanel(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_TC_G01_03_contains_text_widget(self):
        """LogPanel 내부에 Text 위젯이 존재한다."""
        child_types = [type(w).__name__ for w in self.panel.winfo_children()]
        self.assertIn('Text', child_types)

    def test_TC_G01_04_append_inserts_text(self):
        """append() 후 Text 위젯에 해당 문자열이 삽입된다."""
        self.panel.append("test line")
        content = self.panel.text_widget.get('1.0', 'end-1c')
        self.assertIn("test line", content)


class TestBaseLayout(unittest.TestCase):

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.layout = BaseLayout(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_TC_G01_05_column_weight_ratio(self):
        """left:right 컬럼 weight 가 1:2 다."""
        lw = self.root.grid_columnconfigure(0)['weight']
        rw = self.root.grid_columnconfigure(1)['weight']
        self.assertEqual(lw, 1)
        self.assertEqual(rw, 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
