from __future__ import annotations

import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk



import database


class SmartShoppingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Smart Shopping Prototype")
        self.root.geometry("980x680")
        self.root.configure(bg="#fff4f6")

        self.current_customer_id: int | None = None
        self.current_session_id: int | None = None

        self.selected_customer = tk.StringVar()
        self.status_text = tk.StringVar(
            value="Create or choose a customer to start a shopping session."
        )

        self._build_layout()
        self.refresh_customers()
        self.refresh_products()
        self.refresh_cart()

    def _build_layout(self) -> None:
        header = tk.Frame(self.root, bg="#9d174d", padx=20, pady=16)
        header.pack(fill="x")

        tk.Label(
            header,
            text="AI-Powered Smart Shopping System",
            font=("Georgia", 24, "bold"),
            bg="#9d174d",
            fg="white",
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Tkinter + SQLite starter app with face-image storage hooks for DeepFace",
            font=("Arial", 11),
            bg="#9d174d",
            fg="#ffe4e6",
        ).pack(anchor="w", pady=(6, 0))

        body = tk.Frame(self.root, bg="#fff4f6", padx=18, pady=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_customer_panel(body)
        self._build_store_panel(body)

        footer = tk.Frame(self.root, bg="#fff1f2", padx=18, pady=10)
        footer.pack(fill="x")
        tk.Label(
            footer,
            textvariable=self.status_text,
            bg="#fff1f2",
            fg="#881337",
            font=("Arial", 10, "italic"),
        ).pack(anchor="w")

    def _build_customer_panel(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg="white", bd=1, relief="solid")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.columnconfigure(0, weight=1)

        tk.Label(
            panel,
            text="Customer Session",
            font=("Georgia", 18, "bold"),
            bg="white",
            fg="#831843",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        form = tk.Frame(panel, bg="white")
        form.grid(row=1, column=0, sticky="ew", padx=16)
        form.columnconfigure(1, weight=1)

        tk.Label(form, text="Select Customer", bg="white").grid(
            row=0, column=0, sticky="w", pady=6
        )
        self.customer_combo = ttk.Combobox(
            form, textvariable=self.selected_customer, state="readonly"
        )
        self.customer_combo.grid(row=0, column=1, sticky="ew", pady=6)

        tk.Label(form, text="New Customer Name", bg="white").grid(
            row=1, column=0, sticky="w", pady=6
        )
        self.name_entry = tk.Entry(form)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=6)

        action_row = tk.Frame(panel, bg="white")
        action_row.grid(row=2, column=0, sticky="ew", padx=16, pady=10)

        tk.Button(
            action_row,
            text="Create Customer",
            command=self.create_customer,
            bg="#ec4899",
            fg="white",
            padx=10,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            action_row,
            text="Attach Face Image",
            command=self.attach_face_image,
            bg="#db2777",
            fg="white",
            padx=10,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            action_row,
            text="Start Session",
            command=self.start_session,
            bg="#9d174d",
            fg="white",
            padx=10,
        ).pack(side="left")

        self.customer_details = tk.Label(
            panel,
            text="No active customer",
            justify="left",
            anchor="w",
            bg="#fff1f2",
            fg="#881337",
            padx=12,
            pady=12,
            font=("Arial", 10),
        )
        self.customer_details.grid(row=3, column=0, sticky="ew", padx=16, pady=(8, 10))

        help_box = tk.Label(
            panel,
            text=(
                "DeepFace integration point:\n"
                "1. capture customer image\n"
                "2. compare with saved images in faces/\n"
                "3. map match to customer record"
            ),
            justify="left",
            anchor="w",
            bg="#fdf2f8",
            fg="#9d174d",
            padx=12,
            pady=12,
            font=("Arial", 10),
        )
        help_box.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 16))

    def _build_store_panel(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg="white", bd=1, relief="solid")
        panel.grid(row=0, column=1, sticky="nsew")
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(2, weight=1)

        tk.Label(
            panel,
            text="Store Demo",
            font=("Georgia", 18, "bold"),
            bg="white",
            fg="#831843",
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 8))

        top = tk.Frame(panel, bg="white")
        top.grid(row=1, column=0, sticky="ew", padx=16)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)

        self.product_list = tk.Listbox(top, height=10, exportselection=False)
        self.product_list.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        action_panel = tk.Frame(top, bg="#fdf2f8", padx=12, pady=12)
        action_panel.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            action_panel,
            text="Prototype actions",
            font=("Arial", 12, "bold"),
            bg="#fdf2f8",
            fg="#9d174d",
        ).pack(anchor="w")

        tk.Button(
            action_panel,
            text="Add Selected Product To Cart",
            command=self.add_selected_product,
            bg="#be185d",
            fg="white",
            pady=6,
        ).pack(fill="x", pady=(10, 8))

        tk.Label(
            action_panel,
            text=(
                "In your final system, YOLO can trigger the\n"
                "same add-to-cart function after product detection."
            ),
            justify="left",
            anchor="w",
            bg="#fdf2f8",
            fg="#6b213f",
        ).pack(anchor="w")

        cart_frame = tk.Frame(panel, bg="white")
        cart_frame.grid(row=2, column=0, sticky="nsew", padx=16, pady=16)
        cart_frame.columnconfigure(0, weight=1)
        cart_frame.rowconfigure(1, weight=1)

        tk.Label(
            cart_frame,
            text="Live Cart",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#9d174d",
        ).grid(row=0, column=0, sticky="w")

        self.cart_tree = ttk.Treeview(
            cart_frame,
            columns=("product", "category", "qty", "price", "total"),
            show="headings",
            height=10,
        )
        self.cart_tree.grid(row=1, column=0, sticky="nsew", pady=(8, 8))

        for column, text, width in (
            ("product", "Product", 150),
            ("category", "Category", 120),
            ("qty", "Qty", 60),
            ("price", "Price", 90),
            ("total", "Line Total", 110),
        ):
            self.cart_tree.heading(column, text=text)
            self.cart_tree.column(column, width=width, anchor="center")

        bottom = tk.Frame(cart_frame, bg="white")
        bottom.grid(row=2, column=0, sticky="ew")
        bottom.columnconfigure(0, weight=1)

        self.total_label = tk.Label(
            bottom,
            text="Total: Rs 0.00",
            bg="white",
            fg="#831843",
            font=("Georgia", 16, "bold"),
        )
        self.total_label.grid(row=0, column=0, sticky="w")

        tk.Button(
            bottom,
            text="Checkout",
            command=self.checkout,
            bg="#16a34a",
            fg="white",
            padx=16,
            pady=6,
        ).grid(row=0, column=1, sticky="e")

    def refresh_customers(self) -> None:
        customers = database.list_customers()
        self.customer_map = {
            f"{row['id']} - {row['name']}": row["id"] for row in customers
        }
        self.customer_combo["values"] = list(self.customer_map.keys())

    def refresh_products(self) -> None:
        self.products = database.list_products()
        self.product_list.delete(0, tk.END)
        for row in self.products:
            self.product_list.insert(
                tk.END, f"{row['name']} | {row['category']} | Rs {row['price']:.2f}"
            )

    def refresh_cart(self) -> None:
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        if not self.current_session_id:
            self.total_label.config(text="Total: Rs 0.00")
            return

        items = database.get_cart_items(self.current_session_id)
        for row in items:
            self.cart_tree.insert(
                "",
                tk.END,
                values=(
                    row["name"],
                    row["category"],
                    row["quantity"],
                    f"Rs {row['price']:.2f}",
                    f"Rs {row['line_total']:.2f}",
                ),
            )

        total = database.get_cart_total(self.current_session_id)
        self.total_label.config(text=f"Total: Rs {total:.2f}")

    def create_customer(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Enter a customer name first.")
            return

        customer_id = database.create_customer(name)
        self.name_entry.delete(0, tk.END)
        self.refresh_customers()
        self.current_customer_id = customer_id
        self.status_text.set(f"Customer '{name}' created successfully.")
        self._update_customer_details()

    def attach_face_image(self) -> None:
        customer_id = self._resolve_selected_customer_id()
        if not customer_id:
            messagebox.showinfo(
                "Select customer", "Select or create a customer before attaching an image."
            )
            return

        path = filedialog.askopenfilename(
            title="Choose face image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        source = Path(path)
        target = database.FACES_DIR / f"customer_{customer_id}{source.suffix.lower()}"
        shutil.copy(source, target)
        database.update_customer_face_path(customer_id, str(target))

        self.current_customer_id = customer_id
        self.status_text.set("Face image attached. Ready for future DeepFace matching.")
        self._update_customer_details()

    def start_session(self) -> None:
        customer_id = self._resolve_selected_customer_id()
        if not customer_id:
            messagebox.showwarning("No customer", "Select or create a customer first.")
            return

        self.current_customer_id = customer_id
        self.current_session_id = database.start_session(customer_id)
        self.status_text.set(
            f"Started shopping session #{self.current_session_id} for customer #{customer_id}."
        )
        self._update_customer_details()
        self.refresh_cart()

    def add_selected_product(self) -> None:
        if not self.current_session_id:
            messagebox.showwarning(
                "No session", "Start a customer session before adding products."
            )
            return

        selection = self.product_list.curselection()
        if not selection:
            messagebox.showinfo("Choose product", "Select a product from the list.")
            return

        product = self.products[selection[0]]
        database.add_item_to_cart(self.current_session_id, product["id"])
        self.status_text.set(
            f"Added {product['name']} to session #{self.current_session_id}."
        )
        self.refresh_cart()

    def checkout(self) -> None:
        if not self.current_session_id:
            messagebox.showinfo("No session", "There is no active shopping session.")
            return

        total = database.get_cart_total(self.current_session_id)
        database.checkout_session(self.current_session_id)
        messagebox.showinfo(
            "Checkout complete",
            f"Session #{self.current_session_id} checked out successfully.\nTotal bill: Rs {total:.2f}",
        )
        self.status_text.set(
            f"Checkout complete for session #{self.current_session_id}. Total bill Rs {total:.2f}."
        )
        self.current_session_id = None
        self.refresh_cart()
        self._update_customer_details()

    def _resolve_selected_customer_id(self) -> int | None:
        if self.current_customer_id:
            return self.current_customer_id

        selected = self.selected_customer.get().strip()
        if selected:
            return self.customer_map.get(selected)
        return None

    def _update_customer_details(self) -> None:
        if not self.current_customer_id:
            self.customer_details.config(text="No active customer")
            return

        customer = database.get_customer(self.current_customer_id)
        if not customer:
            self.customer_details.config(text="No active customer")
            return

        details = [
            f"Customer ID: {customer['id']}",
            f"Name: {customer['name']}",
            f"Face image: {customer['face_image_path'] or 'Not attached yet'}",
            f"Current session: {self.current_session_id or 'Not started'}",
        ]
        self.customer_details.config(text="\n".join(details))
   



def launch_app() -> None:
    root = tk.Tk()
    SmartShoppingApp(root)
    root.mainloop()


if __name__ == "__main__":
    import database
    database.init_database()
    launch_app()