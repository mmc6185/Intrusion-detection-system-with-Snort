$(document).ready(function () {
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    $('#dashboard-link').on('click', loadDashboard);
    $('#alerts-link').on('click', loadAlerts);
    $('#reports-link').on('click', loadReports);
    $('#settings-link').on('click', loadSettings);

    // Varsayılan olarak dashboard yüklensin
    loadDashboard();
});

function loadDashboard() {
    $('#main-content').html(`
        <div class="row">
            <div class="col-lg-3 col-md-6">
                <div class="card text-white bg-primary mb-3">
                    <div class="card-body">
                        <div class="card-title">Toplam Uyarılar</div>
                        <h2>1234</h2>
                    </div>
                </div>
            </div>
            <div class="col-lg-9">
                <canvas id="alertsChart"></canvas>
            </div>
        </div>
    `);

    // Grafik verilerini yükle
    var ctx = document.getElementById('alertsChart').getContext('2d');
    var alertsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
            datasets: [{
                label: 'Uyarı Sayısı',
                data: [12, 19, 3, 5, 2, 3],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor:'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        }
    });
}

function loadAlerts() {
    $('#main-content').html(`
        <h2>Uyarılar</h2>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Zaman</th>
                    <th>Kaynak IP</th>
                    <th>Hedef IP</th>
                    <th>Protokol</th>
                    <th>Özet</th>
                </tr>
            </thead>
            <tbody id="alertsTableBody">
                <!-- Uyarı verileri buraya yüklenecek -->
            </tbody>
        </table>
    `);

    // Örnek veri ekleyelim
    var alertsData = [
        { time: '2023-09-01 12:00', srcIP: '192.168.1.1', destIP: '10.0.0.1', protocol: 'TCP', summary: 'Port Scan' },
        // Diğer veriler...
    ];

    alertsData.forEach(function(alert) {
        $('#alertsTableBody').append(`
            <tr>
                <td>${alert.time}</td>
                <td>${alert.srcIP}</td>
                <td>${alert.destIP}</td>
                <td>${alert.protocol}</td>
                <td>${alert.summary}</td>
            </tr>
        `);
    });
}

function loadReports() {
    $('#main-content').html(`
        <h2>Raporlar</h2>
        <div class="row">
            <div class="col-lg-6">
                <canvas id="protocolChart"></canvas>
            </div>
            <div class="col-lg-6">
                <canvas id="threatLevelChart"></canvas>
            </div>
        </div>
    `);

    // Protokol dağılım grafiği
    var ctx1 = document.getElementById('protocolChart').getContext('2d');
    var protocolChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            labels: ['TCP', 'UDP', 'ICMP'],
            datasets: [{
                data: [60, 30, 10],
                backgroundColor: ['#007bff', '#dc3545', '#ffc107']
            }]
        }
    });

    // Tehdit seviyesi grafiği
    var ctx2 = document.getElementById('threatLevelChart').getContext('2d');
    var threatLevelChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: ['Düşük', 'Orta', 'Yüksek'],
            datasets: [{
                label: 'Tehdit Seviyesi',
                data: [15, 25, 5],
                backgroundColor: ['#28a745', '#ffc107', '#dc3545']
            }]
        }
    });
}

function loadSettings() {
    $('#main-content').html(`
        <h2>Ayarlar</h2>
        <form>
            <div class="mb-3">
                <label for="update-rules" class="form-label">Kuralları Güncelle</label>
                <button id="update-rules" class="btn btn-primary ms-3">Güncelle</button>
            </div>
            <div class="mb-3">
                <label for="notification-email" class="form-label">Bildirim E-postası</label>
                <input type="email" class="form-control" id="notification-email" placeholder="ornek@eposta.com">
            </div>
            <button type="submit" class="btn btn-success">Kaydet</button>
        </form>
    `);

    $('#update-rules').on('click', function(e) {
        e.preventDefault();
        alert('Kurallar güncellendi!');
    });
}
