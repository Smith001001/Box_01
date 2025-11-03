import tkinter as tk
from tkinter import ttk
import math
import ast

class SafeEval:
	allowed_nodes = {
		ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Load, ast.Constant,
		ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv,
		ast.Call, ast.Name, ast.USub, ast.UAdd
	}
	allowed_names = {
		"sqrt": math.sqrt,
		"sin": math.sin,
		"cos": math.cos,
		"tan": math.tan,
		"log": math.log,
		"ln": math.log,
		"pi": math.pi,
		"e": math.e,
		"abs": abs,
		"pow": pow
	}

	@classmethod
	def eval(cls, expr: str):
		expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**")
		try:
			node = ast.parse(expr, mode="eval")
		except Exception as e:
			raise ValueError("表达式错误") from e
		if not cls._is_allowed(node):
			raise ValueError("包含不支持的表达式")
		return eval(compile(node, "<expr>", "eval"), {"__builtins__": {}}, cls.allowed_names)

	@classmethod
	def _is_allowed(cls, node):
		if type(node) not in cls.allowed_nodes:
			if not (isinstance(node, ast.Constant) and isinstance(node.value, (int, float))):
				return False
		for child in ast.iter_child_nodes(node):
			if isinstance(child, ast.Name) and child.id not in cls.allowed_names:
				return False
			if not cls._is_allowed(child):
				return False
		return True


class CalculatorApp:
	def __init__(self, root: tk.Tk):
		self.root = root
		self.root.title("简洁计算器")
		self.root.geometry("360x520")
		self.root.minsize(320, 480)
		self.root.configure(bg="#0f172a")

		self.display_var = tk.StringVar(value="")
		self.semicolon_mode = False  # 分号模式（保留以便后续切换，用按钮或功能键控制）

		self._setup_style()
		self._build_ui()
		self._bind_keys()

	def _setup_style(self):
		style = ttk.Style()
		try:
			style.theme_use("clam")
		except Exception:
			pass

		self.bg = "#0f172a"
		self.panel_bg = "#111827"
		self.text_fg = "#e5e7eb"
		self.key_fg = "#e5e7eb"
		self.key_bg = "#1f2937"
		self.key_bg_hover = "#374151"
		self.key_accent = "#2563eb"
		self.key_accent_hover = "#1d4ed8"
		self.key_warn = "#ef4444"
		self.key_equal = "#10b981"
		self.key_equal_hover = "#059669"

		style.configure("App.TFrame", background=self.bg)
		style.configure("Panel.TFrame", background=self.panel_bg)
		style.configure("Display.TEntry",
			fieldbackground=self.panel_bg,
			foreground=self.text_fg,
			padding=(12, 10))
		style.configure("Key.TButton",
			background=self.key_bg,
			foreground=self.key_fg,
			font=("Segoe UI", 14),
			padding=(8, 10),
			borderwidth=0)
		style.map("Key.TButton", background=[("active", self.key_bg_hover)])

		style.configure("Op.TButton",
			background=self.key_accent,
			foreground="#ffffff",
			font=("Segoe UI", 14, "bold"))
		style.map("Op.TButton", background=[("active", self.key_accent_hover)])

		style.configure("Warn.TButton",
			background=self.key_warn,
			foreground="#ffffff",
			font=("Segoe UI", 14, "bold"))
		style.map("Warn.TButton", background=[("active", "#dc2626")])

		style.configure("Equal.TButton",
			background=self.key_equal,
			foreground="#0b2320",
			font=("Segoe UI", 16, "bold"))
		style.map("Equal.TButton", background=[("active", self.key_equal_hover)])

	def _build_ui(self):
		container = ttk.Frame(self.root, style="App.TFrame", padding=16)
		container.pack(fill="both", expand=True)

		display_frame = ttk.Frame(container, style="Panel.TFrame", padding=(12, 12))
		display_frame.pack(fill="x", side="top")

		self.entry = ttk.Entry(display_frame, textvariable=self.display_var, style="Display.TEntry",
			font=("Segoe UI", 28, "bold"), justify="right")
		self.entry.pack(fill="x")
		self.entry.focus_set()

		keypad = ttk.Frame(container, style="App.TFrame")
		keypad.pack(fill="both", expand=True, pady=(12, 0))

		for i in range(6):
			keypad.rowconfigure(i, weight=1, uniform="row")
		for j in range(4):
			keypad.columnconfigure(j, weight=1, uniform="col")

		# 第一行
		self._mk_btn(keypad, "C", 0, 0, style="Warn.TButton", cmd=self.clear_all)
		self._mk_btn(keypad, "⌫", 0, 1, style="Op.TButton", cmd=self.backspace)
		self._mk_btn(keypad, "%", 0, 2, style="Op.TButton", cmd=self.percent)
		self._mk_btn(keypad, "÷", 0, 3, style="Op.TButton", cmd=lambda: self.insert_text("÷"))

		# 第二行
		self._mk_btn(keypad, "√", 1, 0, cmd=self.insert_sqrt)
		self._mk_btn(keypad, "x²", 1, 1, cmd=self.insert_square)
		self._mk_btn(keypad, "^", 1, 2, cmd=lambda: self.insert_text("^"))
		self._mk_btn(keypad, "×", 1, 3, style="Op.TButton", cmd=lambda: self.insert_text("×"))

		# 数字与运算
		self._mk_btn(keypad, "7", 2, 0, cmd=lambda: self.insert_text("7"))
		self._mk_btn(keypad, "8", 2, 1, cmd=lambda: self.insert_text("8"))
		self._mk_btn(keypad, "9", 2, 2, cmd=lambda: self.insert_text("9"))
		self._mk_btn(keypad, "−", 2, 3, style="Op.TButton", cmd=lambda: self.insert_text("−"))

		self._mk_btn(keypad, "4", 3, 0, cmd=lambda: self.insert_text("4"))
		self._mk_btn(keypad, "5", 3, 1, cmd=lambda: self.insert_text("5"))
		self._mk_btn(keypad, "6", 3, 2, cmd=lambda: self.insert_text("6"))
		self._mk_btn(keypad, "+", 3, 3, style="Op.TButton", cmd=lambda: self.insert_text("+"))

		self._mk_btn(keypad, "1", 4, 0, cmd=lambda: self.insert_text("1"))
		self._mk_btn(keypad, "2", 4, 1, cmd=lambda: self.insert_text("2"))
		self._mk_btn(keypad, "3", 4, 2, cmd=lambda: self.insert_text("3"))
		self._mk_btn(keypad, "=", 4, 3, style="Equal.TButton", cmd=self.evaluate)

		self._mk_btn(keypad, ".", 5, 0, cmd=lambda: self.insert_text("."))
		self._mk_btn(keypad, "0", 5, 1, cmd=lambda: self.insert_text("0"))
		self._mk_btn(keypad, "(", 5, 2, cmd=lambda: self.insert_text("("))
		self._mk_btn(keypad, ")", 5, 3, cmd=lambda: self.insert_text(")"))

	def _mk_btn(self, parent, text, row, col, cmd=None, style="Key.TButton"):
		btn = ttk.Button(parent, text=text, command=cmd, style=style, takefocus=False)
		btn.grid(row=row, column=col, sticky="nsew", padx=6, pady=6, ipady=6)
		return btn

	def insert_text(self, txt: str):
		if self.entry.selection_present():
			self.entry.delete("sel.first", "sel.last")
		self.entry.insert(tk.INSERT, txt)

	def insert_sqrt(self):
		if self.entry.selection_present():
			start = self.entry.index("sel.first")
			end = self.entry.index("sel.last")
			sel = self.entry.get()[int(start):int(end)]
			self.entry.delete("sel.first", "sel.last")
			self.entry.insert(start, f"sqrt({sel})")
			self.entry.icursor(int(start) + 5 + len(sel))
		else:
			self.entry.insert(tk.INSERT, "sqrt()")
			self.entry.icursor(self.entry.index(tk.INSERT) - 1)

	def insert_square(self):
		self.insert_text("^2")

	def backspace(self):
		if self.entry.selection_present():
			self.entry.delete("sel.first", "sel.last")
		else:
			pos = self.entry.index(tk.INSERT)
			if pos > 0:
				self.entry.delete(pos - 1)

	def delete_forward(self):
		if self.entry.selection_present():
			self.entry.delete("sel.first", "sel.last")
		else:
			pos = self.entry.index(tk.INSERT)
			self.entry.delete(pos)

	def clear_all(self):
		self.display_var.set("")
		self.entry.icursor(tk.END)

	def percent(self):
		if self.entry.selection_present():
			start = self.entry.index("sel.first")
			end = self.entry.index("sel.last")
			text = self.entry.get()[int(start):int(end)]
			try:
				v = float(text) / 100.0
				self.entry.delete("sel.first", "sel.last")
				self.entry.insert(start, self._strip_trailing_zeros(v))
			except Exception:
				pass
			return

		s = self.entry.get()
		i = self.entry.index(tk.INSERT)
		left = i - 1
		while left >= 0 and (s[left].isdigit() or s[left] == "."):
			left -= 1
		left += 1
		right = i
		while right < len(s) and (s[right].isdigit() or s[right] == "."):
			right += 1
		if left < right:
			try:
				v = float(s[left:right]) / 100.0
				self.entry.delete(left, right)
				self.entry.insert(left, self._strip_trailing_zeros(v))
			except Exception:
				pass

	def evaluate(self):
		expr = self.display_var.get().strip()
		if not expr:
			return
		expr = expr.replace(";", "")
		try:
			value = SafeEval.eval(expr)
			self.display_var.set(self._strip_trailing_zeros(value))
			self.entry.icursor(tk.END)
		except Exception:
			self.blink_entry()

	def blink_entry(self):
		def toggle(n=0):
			if n >= 4:
				try:
					self.entry.configure(foreground=self.text_fg)
				except Exception:
					pass
				return
			try:
				self.entry.configure(foreground="#ef4444" if n % 2 == 0 else self.text_fg)
			except Exception:
				pass
			self.root.after(120, lambda: toggle(n + 1))
		toggle()

	def _strip_trailing_zeros(self, num) -> str:
		s = f"{num:.12g}"
		try:
			f = float(s)
			if f.is_integer():
				return str(int(f))
		except Exception:
			pass
		return s

	def toggle_semicolon_mode(self, *_):
		self.semicolon_mode = not self.semicolon_mode
		base = "简洁计算器"
		self.root.title(base + " [分号模式]" if self.semicolon_mode else base)

	def _bind_keys(self):
		# 重要：把键盘拦截绑定到 Entry 上，这样我们能阻止默认行为，避免重复
		self.entry.bind("<Key>", self._on_key)             # 禁用所有字符输入
		self.entry.bind("<Return>", self._on_key)          # 等于运算
		self.entry.bind("<KP_Enter>", self._on_key)        # 小键盘回车
		self.entry.bind("<BackSpace>", self._on_key)       # 删除一个字符（向左）
		self.entry.bind("<Delete>", self._on_key)          # 删除一个字符（向右）

		# 仅保留功能键的全局绑定（可选）
		self.root.bind("<F2>", self.toggle_semicolon_mode)

	def _on_key(self, event: tk.Event):
		# 仅允许：BackSpace、Delete、Return/KP_Enter；其他一律拦截
		if event.keysym in {"Return", "KP_Enter"}:
			self.evaluate()
			return "break"
		if event.keysym == "BackSpace":
			self.backspace()
			return "break"
		if event.keysym == "Delete":
			self.delete_forward()
			return "break"
		# 其余（包括数字、运算符、括号、点、百分号等）全部阻止默认插入
		return "break"


def main():
	root = tk.Tk()
	app = CalculatorApp(root)
	root.mainloop()

if __name__ == "__main__":
	main()