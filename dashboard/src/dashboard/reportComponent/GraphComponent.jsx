import React from 'react';
import { Bar } from 'react-chartjs-2';
import "../../css/graph.css"
import Chart from 'chart.js/auto';
import { CategoryScale } from 'chart.js';
import { ip_address } from '../../base/config';
Chart.register(CategoryScale);
export default class GraphComponent extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      data: [],
      labels: [],
      options: {},
      data_label: "hour",
      month: 0,
      week: 0,
      day: 0
    }
  }

  getRangeType = (type) => {
    if (type === "day") {
      this.setState({
        data_label: "hour",
        option: {
          scales: {
            y: {
              grid: {
                drawBorder: false,
                display: false,
              }
            }
          },
          responsive: true,
          plugins: {
            title: {
              display: true,
              position: 'bottom',
              text: 'Statistic number of people access today',
              font: {
                size: 20
              }
            },
          },
        }
      })
    }
    else if (type === "week") {
      this.setState({
        data_label: "day",
        option: {
          scales: {
            y: {
              grid: {
                drawBorder: false,
                display: false,
              }
            }
          },
          responsive: true,
          plugins: {
            title: {
              display: true,
              position: 'bottom',
              text: 'Statistic number of people access this week',
              font: {
                size: 20
              }
            },
          },
        }
      })
    }
    else if (type === "month") {
      this.setState({
        data_label: "day",
        option: {
          scales: {
            y: {
              grid: {
                drawBorder: false,
                display: false,
              }
            }
          },
          responsive: true,
          plugins: {
            title: {
              display: true,
              position: 'bottom',
              text: 'Statistic number of people access this month',
              font: {
                size: 20
              }
            },
          },
        }
      })
    }

    fetch(`http://10.0.7.88:5000/visualize_v2`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST'
      },
      body: JSON.stringify({ range_type: type })
    })
      .then(response => response.json())
      .then(data => {
        if (type === "day") {
          this.setState({
            labels: data.end_times,
            data: data.counts
          })
        }
        else if (type === "week") {
          this.setState({
            labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            data: data.counts
          })
        }
        else {
          this.setState({
            labels: data.days,
            data: data.counts
          })
        }
      })
      .catch(error => console.log(error))
  }

  updateData = (type) => {
    fetch(`http://10.0.7.88:5000/visualize_v2`, {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ range_type: type })
    })
      .then(response => response.json())
      .then(data => {
        if (type === "day") {
          this.setState({
            day: data.total_count
          })
        }
        else if (type === "week") {
          this.setState({
            week: data.total_count
          })
        }
        else if (type === "month") {
          this.setState({
            month: data.total_count
          })
        }
      })
      .catch(error => {
        console.log(error);
      })
  }

  componentDidMount() {
    this.updateData("month")
    this.updateData("week")
    this.updateData("day")

    this.getRangeType("day")

    setInterval(() => {
      this.updateData("month")
      this.updateData("week")
      this.updateData("day")
    }, 1000 * 60 * 60)
  }

  render() {
    return (
      <div className='dashup'>
        <div className='dash-report'>
          <div className='report-text'>MONTH: {this.state.month + this.state.day}</div>
          <div className='report-text'>WEEK: {this.state.week + this.state.day}</div>
          <div className='report-text'>TODAY: {this.state.day}</div>
        </div>
        <div className='dash-graph'>
          <button onClick={() => this.getRangeType("day")} className="hour-btn">Day</button>
          <button onClick={() => this.getRangeType("week")} className="day-btn">Week</button>
          <button onClick={() => this.getRangeType("month")} className="month-btn">Month</button>

          <Bar
            width={'400%'}
            options={this.state.option}
            data={{
              labels: this.state.labels,
              datasets: [
                {
                  label: this.state.data_label,
                  data: this.state.data,
                  backgroundColor: '#1478BD',
                }
              ]
            }} />
        </div>
      </div>
    );
  }
}
