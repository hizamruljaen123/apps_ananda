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