mycharts = [
    document.getElementById('Chart1').getContext('2d'),
    document.getElementById('Chart2').getContext('2d'),
    document.getElementById('Chart3').getContext('2d'),
    document.getElementById('Chart4').getContext('2d'),
];

chartobjs = [];

for (let i=0;i<4;i++) {
    if(i === 3){
        chartobjs.push(
            new Chart(mycharts[i], {
            type: 'doughnut',
            data: {
            datasets: [{
                data: [90, 10],
                backgroundColor: [
                    'rgba(0, 255, 0, 0.8)',
                    'rgba(255, 0, 0, 0.8)',
                ],
                borderColor: [
                    'rgba(255, 255, 255, 1)',
                    'rgba(255, 255, 255, 1)',
                ],
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: [
                'Accuracy',
                'Loss',
            ]
        },
            options: {
                legend: {
                    display: false,

                 },
                title: {
                    fontSize: 20,
                    text: "Model Accuracy",
                    display: true,
                    fontStyle: 'bold',
                    fontColor: 'black'
                },
            }
        })
        )
    }
    else{
        chartobjs.push(
            new Chart(mycharts[i], {
            type: 'line',
            data: {
                labels: [0,1,2,3,4,5],
                datasets: [{
                    label: '# of Votes',
                    fill: false,
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        type: 'logarithmic',
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        })
    )

    }

}

const chartDict = {'close': chartobjs[0], 'SMA': chartobjs[1], 'EMA':chartobjs[2], 'accuracy': chartobjs[3]}
let count = 59;
const countDiv = document.querySelector(".timer");
function timeCount(){
    if(count === 0){
        count = 60;
    }
    count -= 1;
    countDiv.innerHTML = `${count}s`;
}
// display = {'table': None, 'close': None, 'SMA': None, 'EMA': None, 'accuracy': None, 'date': None}
function updateChart(chart, labels, data){
    chartDict[chart].data.labels = labels;
    chartDict[chart].data.datasets[0].data = data;
}

async function updateDisplay(){
    let tik = document.querySelector('#tik').innerHTML;
    const response = await fetch('/display/'+tik);
    if(response.status === 200){
        const data = await response.json();
        let c = ['close', 'SMA', 'EMA'];
        for (let i = 0; i < 3; i++) {
            updateChart(c[i], data.date, data[c[i]]);
        }
        chartDict['accuracy'].data.datasets[0].data = data.accuracy;
        for (let i = 0; i < chartobjs.length; i++) {
            chartobjs[i].update();
        }
        let table = document.querySelector('.query');
        let mtable = `
            <tr>
              <th>DateTime</th>
              <th>Actual</th>
              <th>Predicted</th>
            </tr>
        `;
        for (let i = 0; i < data.table.Actual.length; i++) {
            mtable += `
                        <tr>
                      <td>${data.table.Datetime[i]}</td>
                      <td>${data.table.Actual[i]}</td>
                      <td>${data.table.Predicted[i]}</td>
                       </tr>
            `
        }
        table.innerHTML = mtable;
    }
}

function allUpdate(){
    timeCount();
    if(count === 0){
        updateDisplay();
    }
}

setInterval(allUpdate, 1000);