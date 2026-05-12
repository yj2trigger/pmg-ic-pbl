"""
gui/log_panel.py — GUI-01

StdoutRedirector : sys.stdout 을 가로채어 콜백으로 전달
LogPanel         : 읽기 전용 CLI 로그 패널 (2/3 영역)
BaseLayout       : 1/3(GUI) + 2/3(LogPanel) 분할 뼈대
"""
import io
import tkinter as tk


class StdoutRedirector(io.TextIOBase):
    """sys.stdout.write() 를 가로채어 callback(text) 로 전달한다."""

    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def write(self, text: str) -> int:
        if text:
            self._callback(text)
        return len(text)

    def flush(self) -> None:
        pass  # 버퍼 없음 — 즉시 전달


class LogPanel(tk.Frame):
    """CLI print() 출력을 실시간으로 표시하는 읽기 전용 스크롤 패널."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._build()

    def _build(self) -> None:
        self._text = tk.Text(
            self,
            state='disabled',
            wrap='char',
            bg='#0D0D0D',
            fg='#B8FFB8',
            font=('Consolas', 10),
            padx=8,
            pady=6,
            relief='flat',
        )
        sb = tk.Scrollbar(self, command=self._text.yview)
        self._text.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        self._text.pack(side='left', fill='both', expand=True)

    def append(self, text: str) -> None:
        """텍스트를 삽입하고 끝으로 자동 스크롤한다."""
        self._text.configure(state='normal')
        self._text.insert('end', text)
        self._text.see('end')
        self._text.configure(state='disabled')

    @property
    def text_widget(self) -> tk.Text:
        return self._text


class BaseLayout:
    """1/3(GUI 컨트롤) + 2/3(CLI 로그) 분할 레이아웃 뼈대."""

    def __init__(self, root: tk.Tk):
        self._root = root
        # grid 비율: column 0 = 1, column 1 = 2
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(0, weight=1)

        self.left_frame = tk.Frame(root, bg='#1C0800')
        self.left_frame.grid(row=0, column=0, sticky='nsew')

        self.log_panel = LogPanel(root, bg='#0D0D0D')
        self.log_panel.grid(row=0, column=1, sticky='nsew')

        self._redirector = StdoutRedirector(self.log_panel.append)

    @property
    def redirector(self) -> StdoutRedirector:
        """sys.stdout 교체용 리다이렉터 인스턴스를 반환한다."""
        return self._redirector
