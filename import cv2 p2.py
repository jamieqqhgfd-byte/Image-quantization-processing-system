import cv2
import tkinter as tk 
from tkinter import filedialog, messagebox 
from PIL import Image, ImageTk 
import numpy as np 

class ImageQuantizerApp: 
    def __init__(self, root): 
        self.root = root 
        self.root.title("作業2-Image Quantization 影像量化") 
        self.root.geometry('1280x720') 
        self.original_img = None 
        self.processed_img = None 
        self.setup_ui() 

    def setup_ui(self): 
        btn_style = {'width': 20, 'height': 1, 'bg': '#C2C2FF', 'font': ('Arial', 12)} 
        
        # 開檔與存檔 
        tk.Button(self.root, text="Select Picture", command=self.load_image, **btn_style).place(x=10, y=10) 
        tk.Button(self.root, text="Save Image", command=self.save_image, **btn_style).place(x=10, y=60) 
 
        # 修改參數輸入框 (Bits 數)
        tk.Label(self.root, text="輸入量化位元 (1/2/4/6):").place(x=10, y=110) 
        self.bits_var = tk.StringVar(value="2") 
        self.e1 = tk.Entry(self.root, textvariable=self.bits_var, font=('Arial', 18), bg='#C2C2FF', width=10) 
        self.e1.place(x=10, y=135) 
 
        # 功能按鈕
        tk.Label(self.root, text="選擇量化算法:", font=('Arial', 10, 'bold')).place(x=10, y=180)
        
        # (1) 教科書之作法 (L-1 levels)
        tk.Button(self.root, text="1. 教科書作法 (L-1)", command=lambda: self.process_quantization(1), **btn_style).place(x=10, y=210) 
        
        # (2) 每一層取最小值
        tk.Button(self.root, text="2. 取最小值 (Min)", command=lambda: self.process_quantization(2), **btn_style).place(x=10, y=250) 
        
        # (3) 每一層取中間值
        tk.Button(self.root, text="3. 取中間值 (Mid)", command=lambda: self.process_quantization(3), **btn_style).place(x=10, y=290) 
 
        # 顯示視窗 
        self.l1 = tk.Label(self.root, text="Original Image") 
        self.l1.place(x=300, y=10) 
        self.l2 = tk.Label(self.root, text="Processed Image") 
        self.l2.place(x=780, y=10) 
 
    def load_image(self): 
        path = filedialog.askopenfilename() 
        if path: 
            img_array = np.fromfile(path, np.uint8)
            self.original_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if self.original_img is not None:
                self.original_img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB) 
                self.display_image(self.original_img, self.l1)
            else:
                messagebox.showerror("錯誤", "無法讀取該圖片，請確認格式。")
 
    def get_bits(self): 
        try: 
            b = int(self.bits_var.get())
            if b <= 0 or b > 8: raise ValueError
            return b
        except: 
            messagebox.showerror("錯誤", "請輸入 1 到 8 之間的整數") 
            return None 
 
    def process_quantization(self, method):
        if self.original_img is None:
            messagebox.showwarning("警告", "請先選擇圖片")
            return
        
        bits = self.get_bits()
        if bits is None: return

        L = 2 ** bits  # 量化階數
        img = self.original_img.astype(np.float32)
        
        if method == 1:
            # 教科書作法: 將 0-255 切成 L-1 個間隔
            # 公式: round(I / (255/(L-1))) * (255/(L-1))
            interval = 255 / (L - 1)
            res = np.round(img / interval) * interval
            
        elif method == 2:
            # 每一層取最小值: 區間長度為 256/L
            # 公式: floor(I / (256/L)) * (256/L)
            interval = 256 / L
            res = np.floor(img / interval) * interval
            
        elif method == 3:
            # 每一層取中間值: 最小值 + 半個區間長度
            # 公式: floor(I / (256/L)) * (256/L) + (interval/2)
            interval = 256 / L
            res = np.floor(img / interval) * interval + (interval / 2)

        self.processed_img = np.clip(res, 0, 255).astype(np.uint8)
        self.display_image(self.processed_img, self.l2)

    def display_image(self, img_array, label): 
        h, w, _ = img_array.shape 
        scale = min(450/w, 450/h) 
        img_pil = Image.fromarray(img_array).resize((int(w*scale), int(h*scale))) 
        img_tk = ImageTk.PhotoImage(img_pil) 
        label.config(image=img_tk) 
        label.image = img_tk 

    def save_image(self): 
        if self.processed_img is not None: 
            path = filedialog.asksaveasfilename(defaultextension=".jpg") 
            if path: 
                # 先轉回 BGR 顏色
                save_img = cv2.cvtColor(self.processed_img, cv2.COLOR_RGB2BGR)
                # 解決中文路徑問題的存法
                ext = path.split('.')[-1]
                res, img_encode = cv2.imencode(f'.{ext}', save_img)
                if res:
                    img_encode.tofile(path)
                    messagebox.showinfo("提示", "儲存成功") 

if __name__ == "__main__": 
    root = tk.Tk() 
    app = ImageQuantizerApp(root) 
    root.mainloop()