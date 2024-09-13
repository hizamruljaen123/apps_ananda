from flask import Flask, render_template, url_for, request, send_from_directory, jsonify
import os
import csv
import subprocess
import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__, template_folder='admin', static_folder='static')

# Mapping dari kolom gejala ke kode singkatan
column_mapping = {
    "Nyeri lambung atau perut bagian atas": "G1",
    "Mual": "G2",
    "Muntah": "G3",
    "Perut kembung": "G4",
    "Gangguan pencernaan": "G5",
    "Nyeri perut yang terasa perih ": "G6",
    "Perdarahan pada tinja atau muntah": "G7",
    "Kehilangan nafsu makan": "G8",
    "Sensasi terbakar pada dada": "G9",
    "Regurgitasi ": "G10"
}

# Mapping dari kode singkatan penyakit ke nama penyakit lengkap
disease_mapping = {
    "P1": "Maag (Gastritis)",
    "P2": "Tukak Lambung (Peptic Ulcer)",
    "P3": "Refluks Gastroesofageal (GERD)",
    "P4": "Penyakit Celiac",
    "P5": "Hepatitis",
    "P6": "Pankreatitis",
    "P7": "Kolitis Ulserativa",
    "P8": "Batu Empedu (Gallstones)",
    "P9": "Sindrom Usus Besar Terirritasi (IBS)",
    "P10": "Kanker Lambung (Stomach Cancer)",
    "P11": "Kanker Usus Besar (Colorectal Cancer)",
    "P12": "Kanker Hati (Liver Cancer)",
    "P13": "Divertikulitis"
}
reverse_disease_mapping = {v: k for k, v in disease_mapping.items()}

# Fungsi untuk memuat decision tree dari JSON
def load_decision_tree(file_path):
    """Memuat decision tree dari file JSON."""
    with open(file_path, 'r') as f:
        decision_tree = json.load(f)
    return decision_tree

# Fungsi untuk menerapkan decision tree ke data uji
def apply_decision_tree(node, test_data):
    """Menerapkan aturan decision tree pada data testing."""
    while 'result' not in node:
        attribute = node.get('attribute')
        value = test_data.get(attribute, None)

        if value is None:
            # Jika data atribut hilang, gunakan jalur default (misal ke kanan)
            print(f"Warning: Missing attribute '{attribute}' in test data. Using default path.")
            node = node['right']  # Default ke cabang 'right' jika nilai tidak ditemukan
            continue

        print(f"Checking node: attribute {attribute}, sample value: {value}, expected value: {node['value']}")

        if value == node['value']:
            node = node['left']
        else:
            node = node['right']

    return node['result']


# Fungsi untuk menyimpan decision tree sebagai JSON
def save_tree_as_json(tree, file_path):
    """Simpan decision tree sebagai file JSON."""
    def node_to_dict(node):
        if node.result is not None:
            return {"result": node.result}
        return {
            "attribute": f"G{node.attribute}",
            "value": node.value,
            "left": node_to_dict(node.left),
            "right": node_to_dict(node.right)
        }
    
    tree_dict = node_to_dict(tree)
    with open(file_path, 'w') as f:
        json.dump(tree_dict, f, indent=4)

# Fungsi CART (pembentukan decision tree)
def gini_impurity(classes):
    total_samples = sum(classes.values())
    impurity = 1
    for cls in classes.values():
        prob_cls = cls / total_samples
        impurity -= prob_cls ** 2
    return impurity

def split_dataset(dataset, attribute, value):
    left_split = [sample for sample in dataset if sample[attribute] == value]
    right_split = [sample for sample in dataset if sample[attribute] != value]
    return left_split, right_split

def class_counts(dataset):
    counts = {}
    for sample in dataset:
        label = sample[-1]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

def information_gain(left_split, right_split, current_impurity):
    p = float(len(left_split)) / (len(left_split) + len(right_split))
    return current_impurity - p * gini_impurity(class_counts(left_split)) - (1 - p) * gini_impurity(class_counts(right_split))

def find_best_split(dataset):
    best_gain = 0
    best_attribute = None
    best_value = None
    current_impurity = gini_impurity(class_counts(dataset))
    n_features = len(dataset[0]) - 1
    for attribute in range(5, n_features):
        values = set(sample[attribute] for sample in dataset)
        for value in values:
            left_split, right_split = split_dataset(dataset, attribute, value)
            if len(left_split) == 0 or len(right_split) == 0:
                continue
            gain = information_gain(left_split, right_split, current_impurity)
            if gain > best_gain:
                best_gain = gain
                best_attribute = attribute
                best_value = value
    return best_gain, best_attribute, best_value

class Node:
    def __init__(self, attribute=None, value=None, left=None, right=None, *, result=None):
        self.attribute = attribute
        self.value = value
        self.left = left
        self.right = right
        self.result = result

def build_tree(dataset, depth=0):
    classes = class_counts(dataset)
    print(f"Classes at depth {depth}: {classes}")  # Debugging print
    node = Node()
    if len(classes) == 1:
        node.result = list(classes.keys())[0]
        print(f"Leaf node created with result: {node.result}")  # Debugging print
        return node
    gain, attribute, value = find_best_split(dataset)
    if gain == 0:
        node.result = max(classes, key=classes.get)
        print(f"Leaf node created due to no gain with result: {node.result}")  # Debugging print
        return node
    left_split, right_split = split_dataset(dataset, attribute, value)
    print(f"Splitting on attribute {attribute} with value {value}")  # Debugging print
    node.attribute = attribute
    node.value = value
    node.left = build_tree(left_split, depth + 1)
    node.right = build_tree(right_split, depth + 1)
    return node


def add_edges(graph, node, parent=None, edge_label='', depth=0):
    if node.result is not None:
        label = f"Prediksi: {node.result}"
    else:
        label = f"Gejala {node.attribute} == {node.value}"
    graph.add_node(id(node), label=label, subset=depth)
    if parent:
        graph.add_edge(parent, id(node), label=edge_label)
    if node.left:
        add_edges(graph, node.left, id(node), 'Ya', depth + 1)
    if node.right:
        add_edges(graph, node.right, id(node), 'Tidak', depth + 1)



@app.route('/classify', methods=['GET'])
def classify():
    """Klasifikasi data uji dengan mengambil data dari static/input/data_uji.xlsx."""
    try:
        # Path ke file data uji (Excel)
        file_path = os.path.join('static', 'input', 'data_uji.xlsx')

        # Load dataset dari Excel
        data_uji = pd.read_excel(file_path)

        # Rename kolom gejala untuk mencocokkan dengan kode G1-G10
        data_uji.rename(columns=column_mapping, inplace=True)

        # Validasi apakah semua kolom gejala ada dalam data uji
        missing_columns = [gejala for gejala in column_mapping.values() if gejala not in data_uji.columns]
        if missing_columns:
            return jsonify({
                "error": "Missing required columns in data_uji",
                "missing_columns": missing_columns
            }), 400

        # Ubah nilai 'Y' menjadi 'Ya' dan 'T' menjadi 'Tidak' untuk setiap kolom gejala
        for gejala in column_mapping.values():
            data_uji[gejala] = data_uji[gejala].replace({'Y': 'Ya', 'T': 'Tidak'})

        # Load decision tree dari file JSON
        decision_tree_path = os.path.join('static', 'output', 'decision_tree.json')
        with open(decision_tree_path, 'r') as f:
            decision_tree = json.load(f)

        # Fungsi untuk melakukan traversal pada decision tree
        def classify_sample(sample, tree):
            """
            Fungsi ini berjalan secara rekursif melalui decision tree berdasarkan nilai sampel.
            tree: node dari decision tree yang sedang dievaluasi
            sample: satu sampel dari data uji, berbentuk dictionary
            """
            while 'result' not in tree:
                attribute = tree.get('attribute')

                # Ambil nilai gejala dari data uji
                value = sample.get(attribute)

                # Debugging - memeriksa nilai yang sedang diuji
                print(f"Checking node: attribute={attribute}, sample value={value}, expected value={tree['value']}")

                # Jika nilai sample tidak ditemukan, tambahkan fallback ke cabang 'right'
                if value is None:
                    print(f"Warning: Missing value for attribute {attribute}. Using default path (right).")
                    tree = tree['right']
                else:
                    # Jika nilai sample cocok dengan nilai node decision tree
                    if value == tree['value']:
                        tree = tree['left']
                    else:
                        tree = tree['right']

            # Mengembalikan hasil prediksi
            return tree['result']

        # Inisialisasi untuk menyimpan hasil prediksi
        results = []

        # Iterasi melalui setiap baris (sampel) di data uji
        for _, row in data_uji.iterrows():
            test_data = row.to_dict()

            # Terapkan decision tree pada setiap sampel
            result_code = classify_sample(test_data, decision_tree)

            # Jika kode penyakit tidak ditemukan dalam disease_mapping, beri warning
            result_full = disease_mapping.get(result_code, f"Unknown disease code: {result_code}")
            results.append(result_full)

        # Return hasil klasifikasi
        return jsonify({
            "message": "Classification successful.",
            "results": results
        })

    except Exception as e:
        # Return error message jika ada masalah
        return jsonify({"error": str(e)}), 500



@app.route('/train', methods=['GET'])
def train():
    """Melatih model dari file static/input/data_latih.xlsx dan menyimpannya."""
    try:
        # Path ke file data latih (Excel)
        file_path = os.path.join('static', 'input', 'data_latih.xlsx')

        # Load dataset dari Excel
        data = pd.read_excel(file_path)

        # Ubah nilai 'Ya' menjadi 1 dan 'Tidak' menjadi 0 untuk kolom gejala
        for gejala in column_mapping.keys():
            data[gejala] = data[gejala].apply(lambda x: 1 if x == 'Ya' else 0)

        # Rename columns using the mapping
        data.rename(columns=column_mapping, inplace=True)

        # Lakukan mapping Diagnosa_Diverse menjadi kode penyakit
        data['Diagnosa_Diverse'] = data['Diagnosa_Diverse'].map(reverse_disease_mapping)

        # Cek apakah mapping berhasil atau ada yang tidak sesuai
        if data['Diagnosa_Diverse'].isnull().any():
            return jsonify({
                "error": "Gagal melakukan mapping Diagnosa_Diverse. Pastikan semua diagnosa sesuai dengan disease_mapping."
            }), 400

        # Convert to list of lists
        dataset = data.values.tolist()

        # Build tree
        tree = build_tree(dataset)

        # Save tree as JSON
        json_output_path = os.path.join('static', 'output', 'decision_tree.json')
        save_tree_as_json(tree, json_output_path)

        # Visualize and save as image
        graph = nx.DiGraph()
        add_edges(graph, tree)
        plt.figure(figsize=(12, 8))
        pos = nx.multipartite_layout(graph, subset_key="subset")
        labels = nx.get_node_attributes(graph, 'label')
        edge_labels = nx.get_edge_attributes(graph, 'label')
        nx.draw(graph, pos, labels=labels, with_labels=True, node_size=1000, node_color='lightblue', font_size=7, arrows=False)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)
        plt.title("Decision Tree for Diagnosing Digestive Diseases")
        plt.axis('off')
        plt.tight_layout()

        image_output_path = os.path.join('static', 'output', 'decision_tree.png')
        plt.savefig(image_output_path)
        plt.close()

        return jsonify({
            "message": "Model has been trained successfully.",
            "json_output": json_output_path,
            "image_output": image_output_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Halaman login
@app.route('/')
def login():
    try:
        return render_template('login.html')
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

# Halaman dashboard
@app.route('/dashboard')
def dashboard():
    """Render halaman dashboard."""
    try:
        main_js_url = url_for('static', filename='js/main.js')
        return render_template('index.html', main_js_url=main_js_url)
    except Exception as e:
        return f"Error loading template: {str(e)}", 500

# Halaman data latih
@app.route('/data_latih')
def data_latih():
    """Render halaman data latih."""
    return render_template('data_latih.html')

# Halaman data uji
@app.route('/data_uji')
def data_uji():
    """Render halaman data uji."""
    return render_template('data_uji.html')

# Halaman nilai importance
@app.route('/nilai_importance')
def nilai_importance():
    """Render halaman nilai importance."""
    return render_template('nilai_importance.html')

# Halaman cart processing
@app.route('/cart_processing')
def cart_processing():
    """Render halaman cart_processing."""
    try:
        main_js_url = url_for('static', filename='js/main.js')
        return render_template('cart_processing.html', main_js_url=main_js_url)
    except Exception as e:
        return f"Error loading template: {str(e)}", 500
    
# Endpoint untuk mengambil data dari data_latih.xlsx dan mengembalikannya sebagai JSON
@app.route('/get_data_latih', methods=['GET'])
def get_data_latih():
    """Mengambil data dari data_latih.xlsx dan mengembalikan sebagai JSON."""
    try:
        file_path = os.path.join('static', 'input', 'data_latih.xlsx')
        data_latih = pd.read_excel(file_path)
        return jsonify(data_latih.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint untuk mengambil data dari data_uji.xlsx dan mengembalikannya sebagai JSON
@app.route('/get_data_uji', methods=['GET'])
def get_data_uji():
    """Mengambil data dari data_uji.xlsx dan mengembalikan sebagai JSON."""
    try:
        file_path = os.path.join('static', 'input', 'data_uji.xlsx')
        data_uji = pd.read_excel(file_path)
        return jsonify(data_uji.to_dict(orient='records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Buka file CSV di Excel
@app.route('/open-csv', methods=['POST'])
def open_csv_in_excel():
    """Buka file CSV menggunakan aplikasi Excel."""
    request_data = request.get_json()
    if 'filename' not in request_data:
        return 'Nama file CSV tidak diberikan', 400

    filename = request_data['filename']
    csv_path = os.path.join(os.path.abspath('input'), filename)

    if os.path.exists(csv_path):
        command = f'start excel.exe "{csv_path}"'
        os.system(command)
        return 'File CSV berhasil dibuka menggunakan Excel'
    else:
        return 'File CSV tidak ditemukan', 404

# Handle akses ke static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Handle akses ke static files."""
    try:
        return send_from_directory(app.static_folder, filename)
    except Exception as e:
        return f"Error accessing static file: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
