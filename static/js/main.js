function fetchDataLatih() {
    fetch('http://127.0.0.1:5000/get_data_latih')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('dataLatihTable').getElementsByTagName('tbody')[0];

        // Clear existing rows
        tableBody.innerHTML = '';

        // Iterate through each data entry and create a table row
        data.forEach((item) => {
            const row = document.createElement('tr');

            // Create table cells for each column
            row.innerHTML = `
                <td>${item.No}</td>
                <td>${item.Alamat}</td>
                <td>${item.Suspek}</td>
                <td>${item.Usia}</td>
                <td>${item['P/L']}</td>
                <td>${item.Mual}</td>
                <td>${item.Muntah}</td>
                <td>${item['Nyeri lambung atau perut bagian atas']}</td>
                <td>${item['Kehilangan nafsu makan']}</td>
                <td>${item['Sensasi terbakar pada dada']}</td>
                <td>${item['Gangguan pencernaan']}</td>
                <td>${item['Nyeri perut yang terasa perih ']}</td>
                <td>${item['Perut kembung']}</td>
                <td>${item['Regurgitasi ']}</td>
                <td>${item['Perdarahan pada tinja atau muntah']}</td>
                <td>${item.Diagnosa_Diverse}</td>
            `;

            // Append the row to the table body
            tableBody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching data:', error));
}
function fetchDataUji() {
    fetch('http://127.0.0.1:5000/get_data_uji')
    .then(response => response.json())
    .then(data => {
        const tableBody = document.getElementById('dataUjiTable').getElementsByTagName('tbody')[0];

        // Clear existing rows
        tableBody.innerHTML = '';

        // Iterate through each data entry and create a table row
        data.forEach((item) => {
            const row = document.createElement('tr');

            // Create table cells for each column
            row.innerHTML = `
                <td>${item.Nama}</td>
                <td>${item.Usia}</td>
                <td>${item['P/L']}</td>
                <td>${item.G1}</td>
                <td>${item.G2}</td>
                <td>${item.G3}</td>
                <td>${item.G4}</td>
                <td>${item.G5}</td>
                <td>${item.G6}</td>
                <td>${item.G7}</td>
                <td>${item.G8}</td>
                <td>${item.G9}</td>
                <td>${item.G10}</td>
            `;

            // Append the row to the table body
            tableBody.appendChild(row);
        });
    })
    .catch(error => console.error('Error fetching data:', error));
}

        // Fungsi untuk menghasilkan warna acak
        function getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        }

        // Fungsi utama untuk menampilkan chart
        async function renderDiagnosaChart() {
            try {
                // Mengambil data dari API
                const response = await fetch('http://localhost:5000/get_data_latih');
                const data = await response.json();
                
                // Menghitung frekuensi Diagnosa_Diverse
                const frequency = data.reduce((acc, item) => {
                    const diagnosa = item.Diagnosa_Diverse;
                    acc[diagnosa] = (acc[diagnosa] || 0) + 1;
                    return acc;
                }, {});

                // Menyiapkan label dan data untuk Chart.js
                const labels = Object.keys(frequency);
                const dataValues = Object.values(frequency);

                // Generate warna acak untuk setiap diagnosa
                const backgroundColors = labels.map(() => getRandomColor());
                const borderColors = backgroundColors.map(color => color); // Bisa menggunakan warna yang sama untuk border

                // Membuat Chart Bar menggunakan Chart.js
                const ctx = document.getElementById('diagnosaChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels, // Nama-nama Diagnosa
                        datasets: [{
                            label: 'Frekuensi Diagnosa',
                            data: dataValues, // Frekuensi masing-masing diagnosa
                            backgroundColor: backgroundColors,
                            borderColor: borderColors,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });

            } catch (error) {
                console.error('Error fetching or processing data:', error);
            }
        }

        async function renderResults() {
            try {
                // Mengambil data dari API get_data_uji dan clasifiy
                const [dataUji, klasifikasi] = await Promise.all([
                    fetch('http://localhost:5000/get_data_uji').then(res => res.json()),
                    fetch('http://localhost:5000/classify').then(res => res.json())
                ]);

                const hasilKlasifikasi = klasifikasi.results;

                // Render tabel hasil klasifikasi
                const tableBody = document.querySelector("#classificationTable tbody");
                tableBody.innerHTML = '';  // Bersihkan isi tabel

                dataUji.forEach((item, index) => {
                    const row = document.createElement('tr');
                    
                    row.innerHTML = `
                        <td>${item.Nama}</td>
                        <td>${item.Usia}</td>
                        <td>${item['P/L']}</td>
                        <td>${item.G1}</td>
                        <td>${item.G2}</td>
                        <td>${item.G3}</td>
                        <td>${item.G4}</td>
                        <td>${item.G5}</td>
                        <td>${item.G6}</td>
                        <td>${item.G7}</td>
                        <td>${item.G8}</td>
                        <td>${item.G9}</td>
                        <td>${item.G10}</td>
                        <td>${hasilKlasifikasi[index]}</td>
                    `;
                    tableBody.appendChild(row);
                });

                // Hitung frekuensi klasifikasi penyakit
                const frequency = hasilKlasifikasi.reduce((acc, result) => {
                    acc[result] = (acc[result] || 0) + 1;
                    return acc;
                }, {});

                // Render chart frekuensi penyakit
                const labels = Object.keys(frequency);
                const dataValues = Object.values(frequency);

                const ctx = document.getElementById('classificationChart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,  // Nama penyakit
                        datasets: [{
                            label: 'Frekuensi Penyakit',
                            data: dataValues,  // Frekuensi tiap penyakit
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });

            } catch (error) {
                console.error('Error fetching or processing data:', error);
            }
        }
