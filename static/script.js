
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
                    fontColor: 'white'
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
                    fontColor: 'white'
                },
            }
        });


let colors = ['225,104,104', '0,128,0', '142, 124, 195']
let names = ['close', 'SMA', 'EMA'];
const capitalize = (s) => {
    if (typeof s !== 'string') return ''
    return s.charAt(0).toUpperCase() + s.slice(1)
};

let chartInfo = {};
for (let i = 0; i < 3; i++) {
    chartInfo[names[i]] = {
                  x: ["2021-02-26 21:59:00+00:00", "2021-02-26 22:00:00+00:00", "2021-02-26 22:01:00+00:00", "2021-02-26 22:02:00+00:00"],
                  y: [16, 5, 11, 9],
                  name: capitalize(names[i]),
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
                }
}

function trim(s){
  return ( s || '' ).replace( /^\s+|\s+$/g, '' );
}

//********* start Line plot build ************************
const mybox = document.querySelector('#line');


var layout = {
    title: "LIVE STOCK CHART " + document.querySelector('#tik').innerHTML,
    autosize: false,
    width: mybox.clientWidth,
    height: mybox.clientHeight-10,
    xaxis: {
        title: 'DateTime',
      }
};

var config = {responsive: true};

var chart_data = [chartInfo.close, chartInfo.SMA, chartInfo.EMA];

Plotly.newPlot('line', chart_data, layout, config);
//********* finish Line plot build ************************

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
    chartInfo[chart].x = labels;
    chartInfo[chart].y = data;
}

async function updateDisplay(){
    let tik = trim(document.querySelector('#tik').innerText);
    const the_ticker = trim(document.querySelector('#the_ticker').innerText);
    console.log(`name: ${tik} \n ticker ${the_ticker}`);
    let obj = {'name': tik, 'ticker': the_ticker};
     let response = await fetch('/display', {method: 'POST', headers: {'Content-Type': 'application/json'},
                                                    body: JSON.stringify(obj)});
//    const response = await fetch('/display/'+tik);
    console.log(response.status)
    if(response.status === 200){
        try{
            const data = await response.json();

        for (let i = 0; i < 3; i++) {
            updateChart(names[i], data.date, data[names[i]]);
        }
        Plotly.redraw('line');
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

        }catch (err){
            console.log('error occurred')
            console.log(err)
        }

    }
    else if (response.status === 404){
        document.body.innerHTML = await response.text();
    }
}

const mySwitcher = {'close': 0, 'SMA': 0, 'EMA': 0};
let n_index = {'close': 0, 'SMA': 1, 'EMA': 2};

function update_index(kind, name){
    if(kind==='push'){
        n_index[name] = chart_data.length - 1;
    }
    else if (kind === 'pop'){
        let n = n_index[name];
        n_index[name] = -1;
        for (let key in n_index){
            if (n_index[key] > n){
                n_index[key] -= 1;
            }
        }
    }
}

function change_chart(name){
    // chart_data
    console.log(name);
    mySwitcher[name] = mySwitcher[name]^1;
        if(mySwitcher[name] === 1){
            chart_data.splice(n_index[name], 1);
            update_index(kind='pop', name=name)
            Plotly.redraw('line');
        }else{
            chart_data.push(chartInfo[name]);
            update_index(kind='push', name=name)
            Plotly.redraw('line');
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