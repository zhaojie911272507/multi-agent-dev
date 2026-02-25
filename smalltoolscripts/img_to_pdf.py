import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import img2pdf


class ImageToPDFConverter:
    """图片转PDF工具"""
    def __init__(self, root):
        self.root = root
        self.root.title("图片转PDF工具")
        self.root.geometry("600x500")

        # 存储图片路径列表
        self.image_paths = []

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_label = tk.Label(self.root, text="图片转PDF工具", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # 添加图片按钮
        add_button = tk.Button(button_frame, text="添加图片", command=self.add_images)
        add_button.grid(row=0, column=0, padx=5)

        # 上移按钮
        up_button = tk.Button(button_frame, text="上移", command=self.move_up)
        up_button.grid(row=0, column=1, padx=5)

        # 下移按钮
        down_button = tk.Button(button_frame, text="下移", command=self.move_down)
        down_button.grid(row=0, column=2, padx=5)

        # 删除按钮
        delete_button = tk.Button(button_frame, text="删除", command=self.delete_image)
        delete_button.grid(row=0, column=3, padx=5)

        # 清空按钮
        clear_button = tk.Button(button_frame, text="清空", command=self.clear_list)
        clear_button.grid(row=0, column=4, padx=5)

        # 列表框架
        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # 列表标签
        list_label = tk.Label(list_frame, text="图片列表 (拖动或使用按钮调整顺序)")
        list_label.pack()

        # 创建列表框和滚动条
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = tk.Scrollbar(list_frame)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # 保存选项框架
        options_frame = tk.Frame(self.root)
        options_frame.pack(pady=10)

        # PDF文件名输入
        tk.Label(options_frame, text="PDF文件名:").grid(row=0, column=0, sticky=tk.W)
        self.filename_var = tk.StringVar(value="output.pdf")
        filename_entry = tk.Entry(options_frame, textvariable=self.filename_var, width=30)
        filename_entry.grid(row=0, column=1, padx=5)

        # 转换按钮
        convert_button = tk.Button(self.root, text="转换为PDF", command=self.convert_to_pdf,
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        convert_button.pack(pady=20)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_images(self):
        filetypes = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("所有文件", "*.*")
        ]

        filenames = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=filetypes
        )

        if filenames:
            for filename in filenames:
                self.image_paths.append(filename)
                self.listbox.insert(tk.END, os.path.basename(filename))

            self.status_var.set(f"已添加 {len(filenames)} 张图片")

    def move_up(self):
        selected = self.listbox.curselection()
        if not selected:
            return

        index = selected[0]
        if index > 0:
            # 交换列表中的位置
            self.image_paths[index], self.image_paths[index - 1] = self.image_paths[index - 1], self.image_paths[index]

            # 更新列表框
            item = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index - 1, item)
            self.listbox.select_set(index - 1)

    def move_down(self):
        selected = self.listbox.curselection()
        if not selected:
            return

        index = selected[0]
        if index < len(self.image_paths) - 1:
            # 交换列表中的位置
            self.image_paths[index], self.image_paths[index + 1] = self.image_paths[index + 1], self.image_paths[index]

            # 更新列表框
            item = self.listbox.get(index)
            self.listbox.delete(index)
            self.listbox.insert(index + 1, item)
            self.listbox.select_set(index + 1)

    def delete_image(self):
        selected = self.listbox.curselection()
        if not selected:
            return

        index = selected[0]
        self.listbox.delete(index)
        self.image_paths.pop(index)

    def clear_list(self):
        if messagebox.askyesno("确认", "确定要清空所有图片吗？"):
            self.listbox.delete(0, tk.END)
            self.image_paths.clear()

    def convert_to_pdf(self):
        if not self.image_paths:
            messagebox.showerror("错误", "请先添加图片")
            return

        filename = self.filename_var.get().strip()
        if not filename:
            messagebox.showerror("错误", "请输入PDF文件名")
            return

        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        # 选择保存位置
        save_path = filedialog.asksaveasfilename(
            title="保存PDF文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf")],
            initialfile=filename
        )

        if not save_path:
            return

        try:
            self.status_var.set("正在转换...")
            self.root.update()

            # 使用img2pdf库将图片转换为PDF
            with open(save_path, "wb") as f:
                f.write(img2pdf.convert(self.image_paths))

            self.status_var.set(f"转换完成: {save_path}")
            messagebox.showinfo("成功", f"PDF文件已保存到:\n{save_path}")

        except Exception as e:
            self.status_var.set("转换失败")
            messagebox.showerror("错误", f"转换过程中发生错误:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageToPDFConverter(root)
    root.mainloop()


if __name__ == "__main__":
    main()