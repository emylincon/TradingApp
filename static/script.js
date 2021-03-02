
let pie = document.getElementById('Pie').getContext('2d');
let pie1 = document.getElementById('Pie1').getContext('2d');
let pieChart = new Chart(pie, {
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
                    text: "Prediction Accuracy",
                    display: true,
                    fontStyle: 'bold',
                    fontColor: 'black'
                },
            }
        });

let pieChart1 = new Chart(pie1, {
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
        });


let colors = ['225,104,104', '0,128,0', '142, 124, 195']
let names = ['close', 'SMA', 'EMA'];

let chartInfo = {};
for (let i = 0; i < 3; i++) {
    chartInfo[names[i]] = {
        'data': [{
                  x: ["2021-02-26 21:59:00+00:00", "2021-02-26 22:00:00+00:00", "2021-02-26 22:01:00+00:00", "2021-02-26 22:02:00+00:00"],
                  y: [16, 5, 11, 9],
                  type: 'scatter',
                    line: {shape: 'spline',
                        dash: 'dashdot',
                        color: 'rgba('+colors[i]+',1)',
                        width: 2
                    },
                    marker: {
                    color: 'rgba('+colors[i]+',0.7)',
                    size: 8
                  },
                }],
        'layout': {
                  title:`${names[i]} ${document.querySelector('#tik').innerHTML}`,
                  xaxis: {
                    title: 'DateTime',
                  },
                  yaxis: {
                    // title: 'Close'
                  },
                    plot_bgcolor:"rgba(233, 231, 231, 0.3)",
                    paper_bgcolor:"rgb(233, 231, 231)"
                }
    }
}

for (let i = 0; i < 3; i++) {
    Plotly.newPlot(names[i], chartInfo[names[i]]['data'], chartInfo[names[i]]['layout']);
}
const no = 59;
let count = 59;
const countDiv = document.querySelector(".timer");
function timeCount(){
    if(count === 0){
        count = no+1;
    }
    count -= 1;
    countDiv.innerHTML = `${count}s`;
}
// display = {'table': None, 'close': None, 'SMA': None, 'EMA': None, 'accuracy': None, 'date': None}
function updateChart(chart, labels, data){
    chartInfo[chart].data[0].x = labels;
    chartInfo[chart].data[0].y = data;

}

async function updateDisplay(){
    let tik = document.querySelector('#tik').innerHTML;
    const response = await fetch('/display/'+tik);
    if(response.status === 200){
        const data = await response.json();

        for (let i = 0; i < 3; i++) {
            updateChart(names[i], data.date, data[names[i]]);
            Plotly.redraw(names[i]);
        }

        pieChart.data.datasets[0].data = data.accuracy;
        pieChart1.data.datasets[0].data = data.model;
        pieChart.update();
        pieChart1.update();
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

updateDisplay();

function allUpdate(){
    timeCount();
    if(count === 0){
        updateDisplay();
    }
}

setInterval(allUpdate, 1000);