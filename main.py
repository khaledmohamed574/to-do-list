"""
To-Do List Desktop Application
Language: Python 3.x
GUI Library: tkinter / ttk
Architecture: Object-Oriented Design (OOP)
Persistence: JSON (tasks.json)
Bilingual Support: English & Arabic with dynamic layout and text direction.

To execute:
    python main.py
"""

import os
import json
import uuid
import datetime
from datetime import datetime as dt
import tkinter as tk
from tkinter import ttk, messagebox

# --- Translation Dictionary for Bilingual Support ---
TRANSLATIONS = {
    'en': {
        'window_title': 'To-Do List Planner (Tkinter Desktop)',
        'search_label': 'Search Title:',
        'search_placeholder': 'Type to search...',
        'lang_toggle': 'العربية (Arabic)',
        'btn_add': 'Add New Task',
        'btn_edit': 'Edit Selected',
        'btn_delete': 'Delete Selected',
        'btn_toggle': 'Toggle Status',
        'lbl_status_filter': 'Status:',
        'lbl_priority_filter': 'Priority:',
        'lbl_sort': 'Sort By:',
        'col_title': 'Task Title',
        'col_due': 'Due Date',
        'col_priority': 'Priority',
        'col_status': 'Status',
        'status_bar_fmt': 'Pending Tasks: {} | Completed Tasks: {}',
        'msg_overdue': 'OVERDUE',
        'confirm_delete': 'Confirm Delete',
        'confirm_delete_msg': 'Are you sure you want to delete this task?',
        'err_validation': 'Validation Error',
        'err_title_empty': 'Task Title cannot be empty!',
        'err_invalid_date': 'Invalid Date Format! Please use YYYY-MM-DD.',
        'dialog_title_add': 'Create New Task',
        'dialog_title_edit': 'Modify Existing Task',
        'lbl_form_title': 'Task Title:',
        'lbl_form_desc': 'Description:',
        'lbl_form_due': 'Due Date (YYYY-MM-DD):',
        'lbl_form_priority': 'Priority Level:',
        'btn_save': 'Save Task',
        'btn_cancel': 'Cancel',
        'filter_all': 'All',
        'filter_pending': 'Pending',
        'filter_completed': 'Completed',
        'prio_high': 'High',
        'prio_medium': 'Medium',
        'prio_low': 'Low'
    },
    'ar': {
        'window_title': 'مخطط المهام المكتبي (واجهة بايثون)',
        'search_label': 'بحث بالعنوان:',
        'search_placeholder': 'اكتب للبحث...',
        'lang_toggle': 'English (الإنجليزية)',
        'btn_add': 'إضافة مهمة جديدة',
        'btn_edit': 'تعديل المهمة',
        'btn_delete': 'حذف المهمة',
        'btn_toggle': 'تغيير الحالة',
        'lbl_status_filter': 'الحالة:',
        'lbl_priority_filter': 'الأهمية:',
        'lbl_sort': 'ترتيب حسب:',
        'col_title': 'عنوان المهمة',
        'col_due': 'تاريخ الاستحقاق',
        'col_priority': 'الأهمية',
        'col_status': 'الحالة',
        'status_bar_fmt': 'المهام المعلقة: {} | المهام المكتملة: {}',
        'msg_overdue': 'متأخرة!',
        'confirm_delete': 'تأكيد الحذف',
        'confirm_delete_msg': 'هل أنت متأكد من رغبتك في حذف هذه المهمة؟',
        'err_validation': 'خطأ في التحقق',
        'err_title_empty': 'لا يمكن أن يكون عنوان المهمة فارغاً!',
        'err_invalid_date': 'صيغة تاريخ غير صالحة! يرجى استخدام الصيغة YYYY-MM-DD.',
        'dialog_title_add': 'إنشاء مهمة جديدة',
        'dialog_title_edit': 'تعديل المهمة الحالية',
        'lbl_form_title': 'عنوان المهمة:',
        'lbl_form_desc': 'الوصف:',
        'lbl_form_due': 'تاريخ الاستحقاق (YYYY-MM-DD):',
        'lbl_form_priority': 'درجة الأهمية:',
        'btn_save': 'حفظ المهمة',
        'btn_cancel': 'إلغاء',
        'filter_all': 'الكل',
        'filter_pending': 'قيد الانتظار',
        'filter_completed': 'مكتمل',
        'prio_high': 'مرتفع',
        'prio_medium': 'متوسط',
        'prio_low': 'منخفض'
    }
}


class Task:
    """
    Represents a single Task entity with modular serialization support.
    """
    def __init__(self, task_id=None, title="", description="", due_date="", priority="Medium", status="Pending", created_at=None):
        self.id = task_id if task_id else str(uuid.uuid4())
        self.title = title
        self.description = description
        self.due_date = due_date  # Format: YYYY-MM-DD
        self.priority = priority  # High, Medium, Low
        self.status = status      # Pending, Completed
        self.created_at = created_at if created_at else datetime.datetime.now().isoformat()

    def to_dict(self):
        """Serializes the Task object into a standard dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Creates a Task instance from a dictionary."""
        return cls(
            task_id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            due_date=data.get("due_date", ""),
            priority=data.get("priority", "Medium"),
            status=data.get("status", "Pending"),
            created_at=data.get("created_at")
        )

    def is_overdue(self):
        """Determines whether a pending task has exceeded its due date."""
        if self.status == "Completed":
            return False
        try:
            due = dt.strptime(self.due_date, "%Y-%m-%d").date()
            return due < datetime.date.today()
        except ValueError:
            return False


class TaskManager:
    """
    Handles CRUD operations, filtration, sorting, searching, and JSON persistence.
    """
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Loads tasks from JSON, handling missing or corrupted files gracefully."""
        if not os.path.exists(self.filename):
            self.tasks = []
            return
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data]
        except (json.JSONDecodeError, IOError, TypeError):
            # Gracefully initialize on corrupted or empty file
            self.tasks = []

    def save_tasks(self):
        """Persists tasks catalog to JSON with error handling."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([t.to_dict() for t in self.tasks], f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, task):
        """Creates a new task and triggers auto-save."""
        self.tasks.append(task)
        self.save_tasks()

    def update_task(self, task_id, updated_fields):
        """Updates task attributes by ID and auto-saves."""
        for task in self.tasks:
            if task.id == task_id:
                for key, val in updated_fields.items():
                    if hasattr(task, key):
                        setattr(task, key, val)
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id):
        """Deletes a task by ID and auto-saves."""
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) < initial_len:
            self.save_tasks()
            return True
        return False

    def toggle_task_status(self, task_id):
        """Toggles state between Pending and Completed."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = "Completed" if task.status == "Pending" else "Pending"
                self.save_tasks()
                return task.status
        return None

    def search_and_filter(self, query="", status_filter="All", priority_filter="All", sort_by="Due Date"):
        """
        Applies searches and filters dynamically, returning a sorted list.
        """
        filtered = self.tasks

        # 1. Search Query (Case Insensitive Title)
        if query:
            filtered = [t for t in filtered if query.lower() in t.title.lower()]

        # 2. Filter Status
        if status_filter != "All":
            filtered = [t for t in filtered if t.status == status_filter]

        # 3. Filter Priority
        if priority_filter != "All":
            filtered = [t for t in filtered if t.priority == priority_filter]

        # 4. Sorting logic
        if sort_by == "Due Date":
            # Handle empty dates gracefully by sorting them last
            filtered = sorted(filtered, key=lambda t: t.due_date if t.due_date else "9999-12-31")
        elif sort_by == "Priority":
            priority_weight = {"High": 1, "Medium": 2, "Low": 3}
            filtered = sorted(filtered, key=lambda t: priority_weight.get(t.priority, 4))
        elif sort_by == "Creation Date":
            filtered = sorted(filtered, key=lambda t: t.created_at, reverse=True)

        return filtered

    def get_counts(self):
        """Returns count of pending vs completed tasks."""
        pending = sum(1 for t in self.tasks if t.status == "Pending")
        completed = sum(1 for t in self.tasks if t.status == "Completed")
        return pending, completed


class TaskApp:
    """
    Tkinter Application controller. Manages UI elements, bilingual updates,
    RTL layout adjustments, and dialogue windows.
    """
    def __init__(self, root):
        self.root = root
        self.manager = TaskManager()
        self.lang = 'en'  # Default language is English

        # Set theme and window style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.root.geometry("850x600")
        self.root.minsize(800, 500)
        
        # Configure grid expansion
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Build Main Frames
        self.create_widgets()
        self.apply_translations()
        self.refresh_task_list()

    def create_widgets(self):
        """Initializes widgets structurally. Layout positioning is handled dynamically in apply_translations."""
        # 1. Top Controls Bar (Search + Language)
        self.top_bar = ttk.Frame(self.root, padding=10)
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.columnconfigure(1, weight=1)

        self.lbl_search = ttk.Label(self.top_bar, font=("Helvetica", 10, "bold"))
        self.entry_search = ttk.Entry(self.top_bar, width=30)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_task_list())

        self.btn_lang = ttk.Button(self.top_bar, command=self.toggle_language)

        # 2. Filter & Sort Panel
        self.filter_panel = ttk.LabelFrame(self.root, padding=10)
        self.filter_panel.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.filter_panel)
        self.combo_status = ttk.Combobox(self.filter_panel, values=["All", "Pending", "Completed"], state="readonly", width=12)
        self.combo_status.set("All")
        self.combo_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        self.lbl_prio = ttk.Label(self.filter_panel)
        self.combo_prio = ttk.Combobox(self.filter_panel, values=["All", "High", "Medium", "Low"], state="readonly", width=12)
        self.combo_prio.set("All")
        self.combo_prio.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        self.lbl_sort = ttk.Label(self.filter_panel)
        self.combo_sort = ttk.Combobox(self.filter_panel, values=["Due Date", "Priority", "Creation Date"], state="readonly", width=15)
        self.combo_sort.set("Due Date")
        self.combo_sort.bind("<<ComboboxSelected>>", lambda e: self.refresh_task_list())

        # 3. Main Tasks View (Treeview)
        self.list_frame = ttk.Frame(self.root, padding=10)
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=10)
        self.root.rowconfigure(2, weight=1)
        self.list_frame.columnconfigure(0, weight=1)
        self.list_frame.rowconfigure(0, weight=1)

        columns = ('id', 'title', 'due_date', 'priority', 'status')
        self.tree = ttk.Treeview(self.list_frame, columns=columns, show='headings', selectmode="browse")
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Hide the system ID column but keep it in data
        self.tree.column('id', width=0, stretch=tk.NO)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Double-click action to toggle task completion status
        self.tree.bind("<Double-1>", self.on_double_click)

        # Config tags for overdue coloring
        self.tree.tag_configure('overdue', foreground='#dc2626', background='#fee2e2')
        self.tree.tag_configure('normal', foreground='#1e293b')

        # 4. Bottom Buttons Section
        self.action_frame = ttk.Frame(self.root, padding=10)
        self.action_frame.grid(row=3, column=0, sticky="ew")

        self.btn_add = ttk.Button(self.action_frame, command=self.open_add_dialog)
        self.btn_edit = ttk.Button(self.action_frame, command=self.open_edit_dialog)
        self.btn_toggle = ttk.Button(self.action_frame, command=self.toggle_selected_status)
        self.btn_delete = ttk.Button(self.action_frame, command=self.delete_selected_task)

        # 5. Status Bar
        self.status_bar = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W, padding=5, font=("Helvetica", 9, "italic"))
        self.status_bar.grid(row=4, column=0, sticky="ew")

    def toggle_language(self):
        """Switches active translation map and triggers reflow of grid widgets (RTL/LTR)."""
        self.lang = 'ar' if self.lang == 'en' else 'en'
        self.apply_translations()
        self.refresh_task_list()

    def apply_translations(self):
        """
        Dynamically adjusts widget placements, columns order, headings, and texts to match selected language.
        Implements custom RTL layouts for widgets grid alignments when 'ar' is active.
        """
        strings = TRANSLATIONS[self.lang]
        self.root.title(strings['window_title'])

        # Top Bar Packing based on RTL (Arabic right-to-left alignment, English left-to-right)
        self.lbl_search.config(text=strings['search_label'])
        self.btn_lang.config(text=strings['lang_toggle'])

        # Reset widgets in Top Bar
        for child in self.top_bar.winfo_children():
            child.grid_forget()

        if self.lang == 'ar':
            # Arabic: Language button is left-most, Search label & entry on right
            self.btn_lang.grid(row=0, column=0, sticky="w")
            self.entry_search.grid(row=0, column=1, sticky="e", padx=5)
            self.lbl_search.grid(row=0, column=2, sticky="e")
        else:
            # English: Search label and entry on left, Language button is right-most
            self.lbl_search.grid(row=0, column=0, sticky="w")
            self.entry_search.grid(row=0, column=1, sticky="w", padx=5)
            self.btn_lang.grid(row=0, column=2, sticky="e")

        # Reflow Filter Panel
        self.lbl_status.config(text=strings['lbl_status_filter'])
        self.lbl_prio.config(text=strings['lbl_priority_filter'])
        self.lbl_sort.config(text=strings['lbl_sort'])

        # Adjust Status and Priority dropdown lists with translated choices
        # Keep internal values but let user experience localized dropdown strings if desired,
        # but here we keep it simple and clean using standard status filtering mapped values.
        for child in self.filter_panel.winfo_children():
            child.grid_forget()

        if self.lang == 'ar':
            # Right-to-Left packing of filters
            self.lbl_sort.grid(row=0, column=0, padx=5, sticky="e")
            self.combo_sort.grid(row=0, column=1, padx=5, sticky="e")
            self.lbl_prio.grid(row=0, column=2, padx=5, sticky="e")
            self.combo_prio.grid(row=0, column=3, padx=5, sticky="e")
            self.lbl_status.grid(row=0, column=4, padx=5, sticky="e")
            self.combo_status.grid(row=0, column=5, padx=5, sticky="e")
        else:
            # Left-to-Right packing
            self.lbl_status.grid(row=0, column=0, padx=5, sticky="w")
            self.combo_status.grid(row=0, column=1, padx=5, sticky="w")
            self.lbl_prio.grid(row=0, column=2, padx=5, sticky="w")
            self.combo_prio.grid(row=0, column=3, padx=5, sticky="w")
            self.lbl_sort.grid(row=0, column=4, padx=5, sticky="w")
            self.combo_sort.grid(row=0, column=5, padx=5, sticky="w")

        # Treeview Headings Translation
        self.tree.heading('title', text=strings['col_title'])
        self.tree.heading('due_date', text=strings['col_due'])
        self.tree.heading('priority', text=strings['col_priority'])
        self.tree.heading('status', text=strings['col_status'])

        # Column text alignment (Right for Arabic, Left for English)
        align = "e" if self.lang == 'ar' else "w"
        self.tree.column('title', width=300, anchor=align)
        self.tree.column('due_date', width=120, anchor="center")
        self.tree.column('priority', width=120, anchor="center")
        self.tree.column('status', width=120, anchor="center")

        # Reflow Action Buttons
        self.btn_add.config(text=strings['btn_add'])
        self.btn_edit.config(text=strings['btn_edit'])
        self.btn_toggle.config(text=strings['btn_toggle'])
        self.btn_delete.config(text=strings['btn_delete'])

        for child in self.action_frame.winfo_children():
            child.grid_forget()

        if self.lang == 'ar':
            # Right-to-Left alignment for action buttons
            self.btn_delete.grid(row=0, column=0, padx=5, sticky="w")
            self.btn_toggle.grid(row=0, column=1, padx=5, sticky="w")
            self.btn_edit.grid(row=0, column=2, padx=5, sticky="e")
            self.btn_add.grid(row=0, column=3, padx=5, sticky="e")
            self.action_frame.columnconfigure(0, weight=1)
            self.action_frame.columnconfigure(3, weight=0)
        else:
            # Left-to-Right alignment
            self.btn_add.grid(row=0, column=0, padx=5, sticky="w")
            self.btn_edit.grid(row=0, column=1, padx=5, sticky="w")
            self.btn_toggle.grid(row=0, column=2, padx=5, sticky="w")
            self.btn_delete.grid(row=0, column=3, padx=5, sticky="e")
            self.action_frame.columnconfigure(0, weight=0)
            self.action_frame.columnconfigure(3, weight=1)

        # Status Bar Anchor Alignment
        self.status_bar.config(anchor="e" if self.lang == 'ar' else "w")

    def refresh_task_list(self):
        """Fetches dynamically matching tasks, filters, and renders in Treeview."""
        # Clear current rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Fetch values
        query = self.entry_search.get()
        status_val = self.combo_status.get()
        prio_val = self.combo_prio.get()
        sort_val = self.combo_sort.get()

        # Map filter options to English values if currently Arabic in dropdown
        # (Though we kept Combobox choices English here to ensure seamless functional logic mapping,
        # we still handle translations properly in this controller method.)
        tasks = self.manager.search_and_filter(
            query=query,
            status_filter=status_val,
            priority_filter=prio_val,
            sort_by=sort_val
        )

        for task in tasks:
            # Localize status & priority labels for visual presentation in columns
            prio_lbl = task.priority
            if self.lang == 'ar':
                if task.priority == "High": prio_lbl = "مرتفع"
                elif task.priority == "Medium": prio_lbl = "متوسط"
                elif task.priority == "Low": prio_lbl = "منخفض"

            status_lbl = task.status
            if self.lang == 'ar':
                status_lbl = "قيد الانتظار" if task.status == "Pending" else "مكتمل"

            overdue_suffix = f" ({TRANSLATIONS[self.lang]['msg_overdue']})" if task.is_overdue() else ""
            title_text = f"{task.title}{overdue_suffix}"

            # Tag row based on overdue state to apply color tags
            row_tag = 'overdue' if task.is_overdue() else 'normal'

            self.tree.insert('', tk.END, values=(
                task.id,
                title_text,
                task.due_date,
                prio_lbl,
                status_lbl
            ), tags=(row_tag,))

        # Update Status Bar counters
        pending, completed = self.manager.get_counts()
        fmt = TRANSLATIONS[self.lang]['status_bar_fmt']
        self.status_bar.config(text=fmt.format(pending, completed))

    def on_double_click(self, event):
        """Toggles state between completed/incomplete upon double clicking."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], 'values')
        task_id = item_values[0]
        self.manager.toggle_task_status(task_id)
        self.refresh_task_list()

    def toggle_selected_status(self):
        """Toggles completion status for currently selected treeview task."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], 'values')
        task_id = item_values[0]
        self.manager.toggle_task_status(task_id)
        self.refresh_task_list()

    def delete_selected_task(self):
        """Asks confirmation before deleting task securely."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], 'values')
        task_id = item_values[0]
        title = item_values[1]

        strings = TRANSLATIONS[self.lang]
        confirm = messagebox.askyesno(strings['confirm_delete'], strings['confirm_delete_msg'])
        if confirm:
            self.manager.delete_task(task_id)
            self.refresh_task_list()

    def open_add_dialog(self):
        """Opens sub-dialog window to capture input validation when adding a task."""
        self.open_task_form_dialog()

    def open_edit_dialog(self):
        """Opens form pre-populated with currently highlighted Task details."""
        selected = self.tree.selection()
        if not selected:
            return
        item_values = self.tree.item(selected[0], 'values')
        task_id = item_values[0]

        # Retrieve full object from manager
        target_task = None
        for t in self.manager.tasks:
            if t.id == task_id:
                target_task = t
                break

        if target_task:
            self.open_task_form_dialog(target_task)

    def open_task_form_dialog(self, task_to_edit=None):
        """Renders standalone Dialog for Task additions or revisions with input validation."""
        strings = TRANSLATIONS[self.lang]
        dialog_title = strings['dialog_title_edit'] if task_to_edit else strings['dialog_title_add']
        
        dialog = tk.Toplevel(self.root)
        dialog.title(dialog_title)
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()

        # Input variables
        var_title = tk.StringVar(value=task_to_edit.title if task_to_edit else "")
        var_desc = tk.StringVar(value=task_to_edit.description if task_to_edit else "")
        var_due = tk.StringVar(value=task_to_edit.due_date if task_to_edit else datetime.date.today().strftime("%Y-%m-%d"))
        var_priority = tk.StringVar(value=task_to_edit.priority if task_to_edit else "Medium")

        # Standard layout padding
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title Form Field
        lbl_t = ttk.Label(frame, text=strings['lbl_form_title'], font=("Helvetica", 10, "bold"))
        lbl_t.pack(anchor="w", pady=(0, 2))
        entry_t = ttk.Entry(frame, textvariable=var_title, width=40)
        entry_t.pack(fill="x", pady=(0, 10))

        # Description Field
        lbl_d = ttk.Label(frame, text=strings['lbl_form_desc'])
        lbl_d.pack(anchor="w", pady=(0, 2))
        entry_d = ttk.Entry(frame, textvariable=var_desc, width=40)
        entry_d.pack(fill="x", pady=(0, 10))

        # Due Date Input
        lbl_due = ttk.Label(frame, text=strings['lbl_form_due'])
        lbl_due.pack(anchor="w", pady=(0, 2))
        entry_due = ttk.Entry(frame, textvariable=var_due, width=20)
        entry_due.pack(anchor="w", pady=(0, 10))

        # Priority Dropdown Combobox
        lbl_p = ttk.Label(frame, text=strings['lbl_form_priority'])
        lbl_p.pack(anchor="w", pady=(0, 2))
        
        prio_choices = ["High", "Medium", "Low"]
        combo_p = ttk.Combobox(frame, values=prio_choices, state="readonly", textvariable=var_priority, width=15)
        combo_p.pack(anchor="w", pady=(0, 15))

        # Validation and Form Saving Actions
        def save_form():
            title_val = var_title.get().strip()
            desc_val = var_desc.get().strip()
            due_val = var_due.get().strip()
            prio_val = var_priority.get()

            # Validation 1: Title Empty check
            if not title_val:
                messagebox.showerror(strings['err_validation'], strings['err_title_empty'], parent=dialog)
                return

            # Validation 2: Date Format YYYY-MM-DD verify
            try:
                dt.strptime(due_val, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(strings['err_validation'], strings['err_invalid_date'], parent=dialog)
                return

            # Proceed saving or updating
            if task_to_edit:
                self.manager.update_task(task_to_edit.id, {
                    "title": title_val,
                    "description": desc_val,
                    "due_date": due_val,
                    "priority": prio_val
                })
            else:
                new_task = Task(
                    title=title_val,
                    description=desc_val,
                    due_date=due_val,
                    priority=prio_val
                )
                self.manager.add_task(new_task)

            self.refresh_task_list()
            dialog.destroy()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", side="bottom", pady=5)

        btn_cancel = ttk.Button(btn_frame, text=strings['btn_cancel'], command=dialog.destroy)
        btn_cancel.pack(side="right", padx=5)

        btn_save = ttk.Button(btn_frame, text=strings['btn_save'], command=save_form)
        btn_save.pack(side="right", padx=5)


if __name__ == "__main__":
    # Initialize UI Window Applet
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
