from bs4 import BeautifulSoup
import lxml
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk, scrolledtext

def html_extraction():
    html_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")])
    if not html_path:
        return None, None  # ou lève une exception, ou gère le cas d'annulation

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "lxml")

    # title extraction
    title = soup.title.string if soup.title else ""

    # body division
    body = soup.body
    divs = body.find_all("div", recursive=False)  # exemple

    return divs, title

class MetadataDialog(simpledialog.Dialog):
    def body(self, master):
        self.result = {}
        tk.Label(master, text="tags (séparés par des virgules) :").grid(row=0, sticky="w")
        self.tags = tk.Entry(master, width=40)
        self.tags.grid(row=0, column=1)
        tk.Label(master, text="Auteurices (séparés par des virgules) :").grid(row=1, sticky="w")
        self.authors = tk.Entry(master, width=40)
        self.authors.grid(row=1, column=1)
        tk.Label(master, text="Parution (YYYY-MM-DD) :").grid(row=2, sticky="w")
        self.pubdate = tk.Entry(master, width=40)
        self.pubdate.grid(row=2, column=1)
        tk.Label(master, text="Lecture (YYYY-MM-DD) :").grid(row=3, sticky="w")
        self.reading = tk.Entry(master, width=40)
        self.reading.grid(row=3, column=1)
        tk.Label(master, text="ISBN :").grid(row=4, sticky="w")
        self.isbn = tk.Entry(master, width=40)
        self.isbn.grid(row=4, column=1)
        tk.Label(master, text="type :").grid(row=5, sticky="w")
        self.type = tk.Entry(master, width=40)
        self.type.insert(0, "fiche de lecture")
        self.type.grid(row=5, column=1)
        return self.tags

    def apply(self):
        self.result = {
            "tags": [t.strip() for t in self.tags.get().split(",") if t.strip()],
            "authors": [a.strip() for a in self.authors.get().split(",") if a.strip()],
            "pubdate": self.pubdate.get().strip(),
            "reading": self.reading.get().strip(),
            "isbn": self.isbn.get().strip(),
            "type": self.type.get().strip(),
        }

class CitationReviewDialog(simpledialog.Dialog):
    def __init__(self, parent, notes):
        self.notes = notes
        self.current = 0
        self.types = ["exemple", "important", "definition", "reference", "a-revoir"]
        self.results = []
        super().__init__(parent, title="Revue des citations")

    def body(self, master):
        self.type_var = tk.StringVar(value=self.types[0])
        self.tags_var = tk.StringVar()
        self.text = scrolledtext.ScrolledText(master, width=80, height=10)
        self.text.grid(row=0, column=0, columnspan=3, pady=5)
        tk.Label(master, text="Type de note :").grid(row=1, column=0, sticky="e")
        self.type_menu = ttk.Combobox(master, textvariable=self.type_var, values=self.types, state="readonly")
        self.type_menu.grid(row=1, column=1, sticky="w")
        tk.Label(master, text="Tags (séparés par des espaces) :").grid(row=2, column=0, sticky="e")
        self.tags_entry = tk.Entry(master, textvariable=self.tags_var, width=50)
        self.tags_entry.grid(row=2, column=1, sticky="w")
        self.chap_label = tk.Label(master, text="")
        self.chap_label.grid(row=3, column=0, columnspan=3, sticky="w")
        self.update_display()
        return self.text

    def update_display(self):
        note = self.notes[self.current]
        self.text.delete("1.0", "end")
        self.text.insert("1.0", note["text"])
        self.chap_label.config(text=f"Chapitre : {note['chapter']}")
        # Affiche les valeurs déjà saisies si elles existent
        if len(self.results) > self.current and self.results[self.current]:
            self.type_var.set(self.results[self.current].get("type", self.types[0]))
            self.tags_var.set(" ".join(self.results[self.current].get("tags", [])))
        else:
            self.type_var.set(self.types[0])   # Réinitialise le type
            self.tags_var.set("")              # Réinitialise les tags


    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="Précédent", width=10, command=self.prev_note).pack(side="left")
        tk.Button(box, text="Suivant", width=10, command=self.next_note).pack(side="left")
        tk.Button(box, text="Terminer", width=10, command=self.ok).pack(side="right")
        box.pack()

    def prev_note(self):
        self.save_current()
        if self.current > 0:
            self.current -= 1
            self.update_display()

    def next_note(self):
        self.save_current()
        if self.current < len(self.notes) - 1:
            self.current += 1
            self.update_display()

    def save_current(self):
        self.tags_var.set(self.tags_entry.get())
        self.type_var.set(self.type_menu.get())

        if len(self.results) <= self.current:
            self.results += [{}] * (self.current - len(self.results) + 1)
        self.results[self.current] = {
            "type": self.type_var.get(),
            "tags": [t for t in self.tags_var.get().split() if t],
            "text": self.text.get("1.0", "end-1c"),
            "chapter": self.notes[self.current]["chapter"]
        }
        print("Sauvegarde:", self.results[self.current])

    def apply(self):
        self.save_current()
        self.result = self.results

def notes_to_markdown(title, meta, citations):
    # Métadonnées
    md = "---\n"
    md += "tags:\n"
    for t in meta["tags"]:
        md += f"  - {t}\n"
    md += "Auteurices:\n"
    for a in meta["authors"]:
        md += f"  - {a}\n"
    if meta["pubdate"]: md += f"Parution: {meta['pubdate']}\n"
    if meta["reading"]: md += f"Lecture: {meta['reading']}\n"
    # Insertion du titre défini au départ
    md += "Référence(s):\n"
    md += f"  - {title}\n"
    if meta["isbn"]: md += f"ISBN: {meta['isbn']}\n"
    if meta["type"]: md += f"type: {meta['type']}\n"
    md += "---\n\n"
    # Encadré livre
    md += "> [!book]\n"
    md += f"> ![[{title}.epub]]\n\n"
    # Citations
    for c in citations:
        # ajout des # dans les tags
        tag_str = " ".join(f"#{t}" for t in c["tags"])
        md += f'> [!{c["type"]}]+ {c["chapter"]}\n {c["text"]}\n> {tag_str}\n\n'
    return md

def main(): 
    root = tk.Tk()
    root.withdraw()

    divs, title = html_extraction()
    citations = citation_library_creation(divs)

    metadata = MetadataDialog(root, title="Entrer les métadonnées").result
    
    citations = CitationReviewDialog(root, citations).result

    md = notes_to_markdown(title, metadata, citations)

    save_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
    if save_path: 
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(md)


if __name__ == "__main__":
    main()