import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import json
import os

def generate_rule(tree, feature_names, class_names, gini_values, node_index=0, rule=''):
    """Rekursif untuk membentuk aturan dari decision tree."""
    if tree.children_left[node_index] == tree.children_right[node_index]:  # leaf node
        class_index = tree.value[node_index].argmax()
        rule += f" THEN Class: {class_names[class_index]} with GINI: {gini_values[node_index]:.5f}"
        return rule
    else:
        feature_index = tree.feature[node_index]
        threshold = tree.threshold[node_index]
        feature_name = feature_names[feature_index]

        left_rule = f"{rule}IF {feature_name} <= {threshold} "
        right_rule = f"{rule}IF {feature_name} > {threshold} "
        left_rule = generate_rule(tree, feature_names, class_names, gini_values, tree.children_left[node_index], left_rule)
        right_rule = generate_rule(tree, feature_names, class_names, gini_values, tree.children_right[node_index], right_rule)

        return [left_rule, right_rule]

def klasifikasi(data_latih_csv, data_uji_csv, nilai_importance_csv, output_dir):
    result = {}
    
    # Validasi keberadaan file
    if not os.path.exists(data_latih_csv) or not os.path.exists(data_uji_csv) or not os.path.exists(nilai_importance_csv):
        raise FileNotFoundError("Salah satu file CSV tidak ditemukan. Pastikan file path sudah benar.")
    
    # Membaca data latih dari file CSV
    data_train = pd.read_csv(data_latih_csv, delimiter=';')

    # Membaca nilai importance dari file CSV
    nilai_importance = pd.read_csv(nilai_importance_csv, delimiter=';')

    # Membuat kamus dari DataFrame nilai_importance
    nilai_importance_dict = nilai_importance.set_index('Gejala').to_dict()['Nilai_Importance']

    # Mengganti nilai gejala dalam DataFrame data_train dengan nilai importance
    for gejala, nilai in nilai_importance_dict.items():
        if gejala in data_train.columns:
            data_train[gejala] *= nilai
        else:
            print(f"Gejala '{gejala}' tidak ditemukan dalam data latih. Melewatinya...")

    # Memisahkan fitur (X) dan label (y) pada data latih
    X_train = data_train.drop('Penyakit', axis=1)
    y_train = data_train['Penyakit']

    # Mengubah variabel kategorikal menjadi numerik dengan one-hot encoding
    X_train = pd.get_dummies(X_train)

    # Inisialisasi dan melatih model CART menggunakan data latih
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    # Visualisasi pohon keputusan
    plt.figure(figsize=(30, 20))  # Menyesuaikan ukuran gambar
    plot_tree(model, feature_names=X_train.columns.tolist(), class_names=list(model.classes_), filled=True)
    plt.savefig(os.path.join(output_dir, 'decision_tree.png'), dpi=300, bbox_inches='tight')

    # Membaca data uji dari file CSV
    data_test = pd.read_csv(data_uji_csv, delimiter=';')

    # Mengubah variabel kategorikal menjadi numerik dengan one-hot encoding
    data_test = pd.get_dummies(data_test)

    # Menambahkan kolom yang hilang pada data uji
    missing_columns = set(X_train.columns) - set(data_test.columns)
    for column in missing_columns:
        data_test[column] = 0

    # Memastikan urutan kolom pada data uji sesuai dengan data latih
    data_test = data_test[X_train.columns]

    # Mengklasifikasi data uji
    predictions = model.predict(data_test)

    result['predictions'] = []

    # Menyimpan informasi hasil klasifikasi dalam list
    for i, (prediction, gini) in enumerate(zip(predictions, model.tree_.impurity)):
        rounded_gini = round(gini, 5)
        result['predictions'].append({
            'Nama': data_test.index[i],
            'Prediksi Penyakit': prediction,
            'Nilai Gini': rounded_gini
        })

    # Generate decision rule
    tree = model.tree_
    feature_names = X_train.columns.tolist()
    class_names = list(model.classes_)
    gini_values = model.tree_.impurity
    decision_rule = generate_rule(tree, feature_names, class_names, gini_values)
    result['decision_rule'] = decision_rule

    # Menambahkan laporan klasifikasi ke dalam hasil
    report = classification_report(y_train, model.predict(X_train), output_dict=True)
    result['classification_report'] = report

    # Menyimpan laporan klasifikasi dalam file teks
    with open(os.path.join(output_dir, 'hasil_klasifikasi.txt'), 'w') as f:
        f.write("Hasil Klasifikasi:\n")
        for prediction_info in result['predictions']:
            f.write(f"Prediksi Penyakit: {prediction_info['Prediksi Penyakit']}, Nilai Gini: {prediction_info['Nilai Gini']}\n")
        f.write("\nLaporan Klasifikasi:\n")
        f.write(classification_report(y_train, model.predict(X_train)))

    return json.dumps(result, indent=4)
