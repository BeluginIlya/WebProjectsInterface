function updateTable(data) {
    var tableBody = $('#history-table tbody');
    tableBody.empty(); // Очищаем текущие данные в теле таблицы

    // Добавляем новые данные
    data.forEach(function (record) {
        var newRow = $('<tr>');
        newRow.append('<td>' + record.PalNo + '</td>');
        newRow.append('<td>' + record.NumProd + '</td>');
        newRow.append('<td>' + record.Timestamp + '</td>');
        newRow.append('<td>' + record.Barcode + '</td>');
        newRow.append('<td>' + record.Product + '</td>');
        newRow.append('<td>' + record.StatusPrint + '</td>');

        tableBody.append(newRow);
    });
}

// Обработка события при подключении к веб-сокету
var socket = new WebSocket('ws://localhost:8000/ws/data_updates/');

socket.onmessage = function (event) {
    console.log('WebSocket message received:', event.data);
    var data = JSON.parse(event.data);
    console.log('Parsed data:', data);
    if (data.type === 'data.updated') {
        console.log('Updating table with data:', data.data);
        updateTable(data.data);
    }
};
