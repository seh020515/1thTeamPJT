function updateClock() {
    const now = new Date();
    const timeString = now.getFullYear() + '-' + 
        String(now.getMonth() + 1).padStart(2, '0') + '-' + 
        String(now.getDate()).padStart(2, '0') + ' ' + 
        String(now.getHours()).padStart(2, '0') + ':' + 
        String(now.getMinutes()).padStart(2, '0') + ':' + 
        String(now.getSeconds()).padStart(2, '0');
    
    const clockElements = document.querySelectorAll('.live-clock');
    clockElements.forEach(el => {
        el.innerText = timeString;
    });
}
setInterval(updateClock, 1000);
updateClock();

setInterval(function() {
    fetch('/danger_status')
    .then(response => response.json())
    .then(data => {
        const cam1Status = document.getElementById('cam1-status');
        if (cam1Status) {
            if (data.danger === true) {
                cam1Status.innerText = "위험";
                cam1Status.style.color = "red";
                cam1Status.style.fontWeight = "bold";
            } else {
                cam1Status.innerText = "정상";
                cam1Status.style.color = "green";
                cam1Status.style.fontWeight = "bold";
            }
        }
    })
    .catch(err => console.log("상태 갱신 실패:", err));
}, 1000);