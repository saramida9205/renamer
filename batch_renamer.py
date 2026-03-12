import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class BatchRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("파일/폴더 일괄 이름 변경 도구")
        self.root.geometry("800x600")

        # 검색 결과 저장용 리스트
        self.search_results = []
        self.selection_vars = []

        self.setup_ui()

    def setup_ui(self):
        # 상단 설정 바
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="검색 경로:").pack(side=tk.LEFT, padx=5)
        self.path_entry = tk.Entry(top_frame, width=40)
        self.path_entry.insert(0, "D:/")
        self.path_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(top_frame, text="경로 선택", command=self.browse_path).pack(side=tk.LEFT, padx=5)

        # 검색 및 이름 변경 입력 프레임
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="기존 이름 (검색어):").grid(row=0, column=0, padx=5, pady=5)
        self.search_keyword = tk.Entry(input_frame, width=20)
        self.search_keyword.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="변경할 이름:").grid(row=0, column=2, padx=5, pady=5)
        self.replace_keyword = tk.Entry(input_frame, width=20)
        self.replace_keyword.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(input_frame, text="검색하기", command=self.search_items, bg="#4CAF50", fg="white").grid(row=0, column=4, padx=10, pady=5)

        # 리스트 영역 (스크롤바 포함)
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 트리 리스트뷰 (상태, 유형, 현재 이름, 경로)
        columns = ("select", "type", "name", "path")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree.heading("select", text="선택")
        self.tree.heading("type", text="유형")
        self.tree.heading("name", text="현재 이름")
        self.tree.heading("path", text="전체 경로")

        self.tree.column("select", width=50, anchor=tk.CENTER)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("path", width=400)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 트리뷰의 항목 클릭 시 선택 상태 반전
        self.tree.bind("<ButtonRelease-1>", self.on_item_click)

        # 하단 제어 바
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill=tk.X)

        tk.Button(bottom_frame, text="전체 선택", command=self.select_all).pack(side=tk.LEFT, padx=10)
        tk.Button(bottom_frame, text="전체 해제", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        self.btn_rename = tk.Button(bottom_frame, text="일괄 이름 변경 실행", command=self.rename_items, bg="#F44336", fg="white", font=("Arial", 10, "bold"))
        self.btn_rename.pack(side=tk.RIGHT, padx=10)

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def search_items(self):
        base_path = self.path_entry.get()
        keyword = self.search_keyword.get()

        if not os.path.exists(base_path):
            messagebox.showerror("오류", "유효한 검색 경로를 설정해 주세요.")
            return

        if not keyword:
            messagebox.showwarning("경고", "검색할 키워드를 입력해 주세요.")
            return

        # 리스트 초기화
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.search_results = []

        try:
            # os.walk를 사용하여 하위 모든 파일/폴더 검색
            for root, dirs, files in os.walk(base_path):
                # 폴더 체크
                for d in dirs:
                    if keyword in d:
                        full_path = os.path.join(root, d)
                        self.add_to_list("Folder", d, full_path)
                
                # 파일 체크
                for f in files:
                    if keyword in f:
                        full_path = os.path.join(root, f)
                        self.add_to_list("File", f, full_path)

            if not self.search_results:
                messagebox.showinfo("알림", f"'{keyword}'가 포함된 항목을 찾을 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"검색 중 오류 발생: {str(e)}")

    def add_to_list(self, item_type, name, full_path):
        # [ ] 체크 표시를 흉내내기 위한 문자표 활용
        item_id = self.tree.insert("", tk.END, values=("☐", item_type, name, full_path))
        self.search_results.append({
            "id": item_id,
            "selected": False,
            "type": item_type,
            "name": name,
            "path": full_path
        })

    def on_item_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        for res in self.search_results:
            if res["id"] == item_id:
                res["selected"] = not res["selected"]
                new_status = "☑" if res["selected"] else "☐"
                self.tree.set(item_id, column="select", value=new_status)
                break

    def select_all(self):
        for res in self.search_results:
            res["selected"] = True
            self.tree.set(res["id"], column="select", value="☑")

    def deselect_all(self):
        for res in self.search_results:
            res["selected"] = False
            self.tree.set(res["id"], column="select", value="☐")

    def rename_items(self):
        target_keyword = self.search_keyword.get()
        replace_with = self.replace_keyword.get()
        
        selected_items = [res for res in self.search_results if res["selected"]]

        if not selected_items:
            messagebox.showwarning("경고", "변경할 항목을 리스트에서 선택해 주세요 (클릭하여 체크).")
            return

        if not replace_with:
            if not messagebox.askyesno("확인", "변경할 이름이 비어있습니다. 검색어를 삭제할까요?"):
                return

        if not messagebox.askyesno("최종 확인", f"총 {len(selected_items)}개의 항목 이름을 변경하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            return

        success_count = 0
        fail_count = 0

        # 이름 변경 시 하위 폴더부터 변경하면 상위 경로가 바뀌어 오류가 날 수 있으므로, 
        # 경로 깊이가 깊은 것부터(긴 것부터) 처리하도록 정렬
        selected_items.sort(key=lambda x: len(x["path"]), reverse=True)

        for res in selected_items:
            old_path = res["path"]
            dir_name = os.path.dirname(old_path)
            old_name = os.path.basename(old_path)
            new_name = old_name.replace(target_keyword, replace_with)
            new_path = os.path.join(dir_name, new_name)

            try:
                os.rename(old_path, new_path)
                success_count += 1
            except Exception as e:
                print(f"Error renaming {old_path}: {e}")
                fail_count += 1

        messagebox.showinfo("결과", f"작업 완료\n성공: {success_count}\n실패: {fail_count}")
        # 리스트 새로고침 (검색 다시 실행)
        self.search_items()

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenamer(root)
    root.mainloop()
