import csv
import tkinter as tk
from tkinter import ttk, messagebox
import time

def read_csv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

def get_genre_columns(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        genre_columns = headers[3:]
    return genre_columns

def create_widgets(root, genres_columns):
    instruction_label = tk.Label(
        root,
        text="Select Your Favorite Genres",
        font=("Helvetica", 16, "bold"),
        fg="blue"
    )
    instruction_label.pack(pady=(10, 5))

    checkbox_frame = ttk.LabelFrame(root, text="Genres")
    checkbox_frame.pack(padx=10, pady=10, fill='x')

    genre_vars = {}
    for genre in genres_columns:
        var = tk.BooleanVar()
        chk = ttk.Checkbutton(checkbox_frame, text=genre, variable=var)
        chk.pack(side='left', padx=5, pady=5)
        genre_vars[genre] = var

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    def on_enter(e):
        e.widget['background'] = 'lightgreen'

    def on_leave(e):
        e.widget['background'] = 'lightgray'

    recommend_btn = tk.Button(
        button_frame,
        text="Recommend",
        command=lambda: recommend(genre_vars, tree, genres_columns)
    )
    recommend_btn.grid(row=0, column=0, padx=10)
    recommend_btn.bind("<Enter>", on_enter)
    recommend_btn.bind("<Leave>", on_leave)

    clear_btn = tk.Button(
        button_frame,
        text="Clear",
        command=lambda: clear_selection(genre_vars, tree)
    )
    clear_btn.grid(row=0, column=1, padx=10)
    clear_btn.bind("<Enter>", on_enter)
    clear_btn.bind("<Leave>", on_leave)

    top5_btn = tk.Button(
        button_frame,
        text="Top 5",
        command=lambda: display_top5(tree, genres_columns, genre_vars)
    )
    top5_btn.grid(row=0, column=2, padx=10)
    top5_btn.bind("<Enter>", on_enter)
    top5_btn.bind("<Leave>", on_leave)

    tree_frame = tk.Frame(root)
    tree_frame.pack(padx=10, pady=10, fill='both', expand=True)

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side='right', fill='y')

    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side='bottom', fill='x')

    tree = ttk.Treeview(
        tree_frame,
        columns=('Title', 'Release Year', 'Rating', 'Genres'),
        show='headings',
        yscrollcommand=tree_scroll_y.set,
        xscrollcommand=tree_scroll_x.set
    )
    tree.heading('Title', text='Title')
    tree.heading('Release Year', text='Release Year')
    tree.heading('Rating', text='Rating')
    tree.heading('Genres', text='Genres')
    tree.pack(fill='both', expand=True)

    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    tree.tag_configure('top_pick', background='lightgreen')

    tree.bind("<Double-1>", lambda event: show_movie_details(tree))

    return tree

def recommend(genre_vars, tree, genres_columns):
    selected_genres = [genre for genre, var in genre_vars.items() if var.get()]

    if not selected_genres:
        display_top5(tree, genres_columns)
        return

    filtered_movies = [
        {
            'Title': movie['Title'],
            'Release Year': movie['Release Year'],
            'Rating': movie['Rating'],
            'Genres': ', '.join([genre for genre in genres_columns if movie.get(genre) == '1'])
        }
        for movie in data
        if all(movie.get(genre) == '1' for genre in selected_genres)
    ]

    if not filtered_movies:
        animate_messagebox("No Results", "No movies found matching your selected genres!")
    else:
        sorted_movies = sorted(filtered_movies, key=lambda x: float(x['Rating']), reverse=True)
        display_movies(tree, sorted_movies, genres_columns, top_pick=sorted_movies[0])

def display_movies(tree, movies, genres_columns, top_pick=None):
    for item in tree.get_children():
        tree.delete(item)

    for movie in movies:
        genres = movie.get('Genres', ', '.join([genre for genre in genres_columns if movie.get(genre) == '1']))
        tree.insert('', 'end', values=(movie['Title'], movie['Release Year'], movie['Rating'], genres))

    if top_pick:
        animate_top_pick(tree, top_pick)

def display_top5(tree, genres_columns, genre_vars=None):
    selected_genres = [genre for genre, var in genre_vars.items() if var.get()] if genre_vars else []

    if selected_genres:
        filtered_movies = [
            {
                'Title': movie['Title'],
                'Release Year': movie['Release Year'],
                'Rating': movie['Rating'],
                'Genres': ', '.join([genre for genre in genres_columns if movie.get(genre) == '1'])
            }
            for movie in data
            if all(movie.get(genre) == '1' for genre in selected_genres)
        ]
        filtered_movies = sorted(filtered_movies, key=lambda x: float(x['Rating']), reverse=True)[:5]
    else:
        filtered_movies = sorted(data, key=lambda x: float(x['Rating']), reverse=True)[:5]
        for movie in filtered_movies:
            movie['Genres'] = ', '.join([genre for genre in genres_columns if movie.get(genre) == '1'])

    display_movies(tree, filtered_movies, genres_columns, top_pick=filtered_movies[0] if filtered_movies else None)

def clear_selection(genre_vars, tree):
    for var in genre_vars.values():
        var.set(False)

    for item in tree.get_children():
        tree.delete(item)

def show_movie_details(tree):
    selected_item = tree.selection()
    if not selected_item:
        return

    movie_details = tree.item(selected_item[0])['values']
    detail_window = tk.Toplevel()
    detail_window.title(movie_details[0])
    detail_window.geometry("400x300")

    tk.Label(detail_window, text=f"Title: {movie_details[0]}", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(detail_window, text=f"Release Year: {movie_details[1]}", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(detail_window, text=f"Rating: {movie_details[2]}", font=("Helvetica", 12)).pack(pady=5)
    tk.Label(detail_window, text=f"Genres: {movie_details[3]}", font=("Helvetica", 12)).pack(pady=5)

def animate_messagebox(title, message):
    box = tk.Toplevel()
    box.title(title)
    box.geometry("300x100")
    box.transient()
    label = tk.Label(box, text=message, font=("Helvetica", 12), wraplength=280, justify="center")
    label.pack(pady=20)
    box.update_idletasks()
    for _ in range(10):
        box.attributes("-alpha", 0.1 * _)
        box.update()
        time.sleep(0.03)
    box.attributes("-alpha", 1.0)
    box.after(1500, box.destroy)

def animate_top_pick(tree, top_pick):
    for _ in range(5):
        for item in tree.get_children():
            if tree.item(item)['values'][0] == top_pick['Title']:
                tree.tag_configure('top_pick', background='yellow')
                tree.item(item, tags=('top_pick',))
                tree.update_idletasks()
                time.sleep(0.2)
                tree.tag_configure('top_pick', background='lightgreen')
                break

def main():
    global data
    file_path = 'movie_dataset.csv'
    data = read_csv(file_path)
    genres_columns = get_genre_columns(file_path)

    root = tk.Tk()
    root.title("Movie Recommendations")
    root.geometry("800x600")

    tree = create_widgets(root, genres_columns)

    root.mainloop()

if __name__ == "__main__":
    main()
