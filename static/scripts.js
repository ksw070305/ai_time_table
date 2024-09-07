document.addEventListener('DOMContentLoaded', function() {
    // Fetch tasks from server and populate event pool
    fetch('/get_tasks')
        .then(response => response.json())
        .then(data => {
            const eventPool = document.getElementById('event-pool');
            data.tasks.forEach(task => {
                const taskDiv = document.createElement('div');
                taskDiv.classList.add('task');
                taskDiv.setAttribute('draggable', 'true');
                taskDiv.innerText = task;
                eventPool.appendChild(taskDiv);

                // Add dragstart event listener
                taskDiv.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', task);
                });
            });
        })
        .catch(error => console.error('Error:', error));

    // Make calendar cells droppable
    function makeCellsDroppable() {
        document.querySelectorAll('#calendar-body td').forEach(cell => {
            cell.addEventListener('dragover', function(e) {
                e.preventDefault();
            });

            cell.addEventListener('drop', function(e) {
                e.preventDefault();
                const task = e.dataTransfer.getData('text/plain');
                const taskDiv = document.createElement('div');
                taskDiv.classList.add('event');
                taskDiv.innerText = task.length > 15 ? task.substring(0, 15) + '...' : task;
                cell.querySelector('.cell-content').appendChild(taskDiv);
            });
        });
    }

    // Generate calendar
    function generateCalendar(month, year) {
        let calendarBody = document.getElementById('calendar-body');
        calendarBody.innerHTML = '';
        let monthAndYear = document.getElementById('monthAndYear');
        monthAndYear.innerHTML = `${year}년 ${month + 1}월`;

        let firstDay = (new Date(year, month)).getDay();
        let daysInMonth = 32 - new Date(year, month, 32).getDate();
        let date = 1;

        for (let i = 0; i < 6; i++) {
            let row = document.createElement('tr');

            for (let j = 0; j < 7; j++) {
                if (i === 0 && j < firstDay) {
                    let cell = document.createElement('td');
                    let cellContent = document.createElement('div');
                    cellContent.classList.add('cell-content');
                    cell.appendChild(cellContent);
                    row.appendChild(cell);
                } else if (date > daysInMonth) {
                    break;
                } else {
                    let cell = document.createElement('td');
                    let cellContent = document.createElement('div');
                    cellContent.classList.add('cell-content');
                    let cellText = document.createElement('span');
                    cellText.innerText = date;
                    cellContent.appendChild(cellText);
                    cell.appendChild(cellContent);
                    row.appendChild(cell);
                    date++;
                }
            }
            calendarBody.appendChild(row);
        }

        makeCellsDroppable();
    }

    let today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();

    generateCalendar(currentMonth, currentYear);

    document.getElementById('save-btn').addEventListener('click', function() {
        let calendarData = [];
        document.querySelectorAll('#calendar-body td').forEach(cell => {
            let tasks = [];
            cell.querySelectorAll('.event').forEach(taskDiv => {
                tasks.push(taskDiv.innerText);
            });
            calendarData.push(tasks);
        });

        console.log(calendarData); // 콘솔에 이중 리스트 형태로 달력 데이터 출력

        // 서버에 데이터 전송
        fetch('/save_calendar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ calendar: calendarData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 데이터 전송 후 다른 페이지로 이동
                window.location.href = '/calendar';
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
