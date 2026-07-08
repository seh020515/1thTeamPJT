/**
 * 사고 로그 전체 상세 조회, 조치완료 및 전체삭제 제어 스크립트
 */

let allRecords = [];
let currentFilterType = '전체';

document.addEventListener("DOMContentLoaded", function() {
    loadLogs();
});

// 서버에서 파일 데이터를 조회해 메모리에 보관
function loadLogs() {
    fetch('/get_logs')
    .then(res => res.json())
    .then(data => {
        allRecords = data;
        filterLogs(currentFilterType); // 기존 선택되어 있던 필터 기준 재출력
    })
    .catch(err => console.error("로그 조회 통신 오류:", err));
}

// 상단 필터 단추를 누를 때 이벤트 처리
function filterLogs(type) {
    currentFilterType = type;
    if (type === '전체') {
        renderTable(allRecords);
    } else {
        const filtered = allRecords.filter(log => log.type === type);
        renderTable(filtered);
    }
}

// 데이터를 조립해서 기록 조회 테이블 안에 주입
function renderTable(logs) {
    const tbody = document.getElementById('records-tbody');
    if (!tbody) return;

    if (logs.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px; color:#999;">해당 유형의 데이터 기록이 비어있습니다.</td></tr>`;
        return;
    }

    let html = '';
    logs.forEach(log => {
        // 미조치 상태일 경우 조치하기 단추 노출, 조치완료인 경우 텍스트 노출
        const actionButton = log.status === '미조치' 
            ? `<button class="btn-status-action" onclick="updateToResolved(${log.id})" style="background:#28a745; color:#fff; border:none; padding:4px 8px; cursor:pointer; border-radius:3px;">조치하기</button>`
            : `<span style="color:#6c757d; font-weight:bold;">완료됨</span>`;

        html += `
            <tr>
                <td>${log.id}</td>
                <td>${log.time}</td>
                <td><span style="font-weight:bold; color:${log.type === '위험진입' ? '#dc3545' : '#333'}">${log.type}</span></td>
                <td>${log.location}</td>
                <td><span class="status-label ${log.status === '미조치' ? 'label-warning' : 'label-success'}">${log.status}</span></td>
                <td>
                    ${actionButton}
                    <button onclick="deleteLogFromRecords(${log.id})" style="background:#dc3545; color:#fff; border:none; padding:4px 8px; cursor:pointer; border-radius:3px; margin-left:5px;">삭제</button>
                </td>
            </tr>
        `;
    });
    tbody.innerHTML = html;
}

// 미조치 -> 조치완료 상태 처리 함수
function updateToResolved(logId) {
    if (confirm("해당 사건을 '조치완료' 상태로 변경하시겠습니까?")) {
        fetch(`/action_log/${logId}`, {
            method: 'POST'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadLogs();
            } else {
                alert("상태 변경 실패: " + data.message);
            }
        })
        .catch(err => console.error("조치 상태 통신 중 에러:", err));
    }
}

// 개별 삭제 함수
function deleteLogFromRecords(logId) {
    if (confirm("해당 사고 로그 기록을 완전히 삭제하시겠습니까?")) {
        fetch(`/delete_log/${logId}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                loadLogs();
            } else {
                alert("삭제 실패: " + data.message);
            }
        })
        .catch(err => console.error("삭제 통신 중 에러 발생:", err));
    }
}

// 전체 삭제 함수
function clearAllLogs() {
    if (confirm("경고: 저장된 모든 사고 로그 기록이 영구 삭제됩니다. 정말로 전체 삭제하시겠습니까?")) {
        fetch('/clear_all_logs', {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert("모든 기록이 깨끗하게 삭제되었습니다.");
                loadLogs();
            } else {
                alert("전체 삭제 실패: " + data.message);
            }
        })
        .catch(err => console.error("전체 삭제 통신 중 에러 발생:", err));
    }
}