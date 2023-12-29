import React from 'react';
import DatePicker from "react-datepicker";
import { registerLocale, setDefaultLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { CSVLink } from 'react-csv';
import vi from 'date-fns/locale/vi';
import { ip_address } from '../../base/config';

registerLocale('vi', vi);
setDefaultLocale('vi');

export default class PeriodComponent extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            time_start: "",
            time_end: "",
            date_start: "",
            date_end: "",
            title: "Duration report by hour for customers coming to IPH",
            data: [],
            header: [],
            cam_mode: "All",
            cam_lists: ["All", "Cam1", "Cam2", "Cam3", "Cam4", "Cam5", "Cam6", "Cam7",
                "Cam8", "Cam9", "Cam10", "Cam11", "Cam12", "Cam13", "Cam14",
                "Cam15", "Cam16", "Cam17", "Cam18", "Cam19", "Cam20", "Cam21"]
        }
    }

    formatTime = (dateString) => {
        const date = new Date(dateString)
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    formatDate = (dateString) => {
        const date = new Date(dateString)
        return date.toLocaleDateString()
    }

    getDataPeriodByCamera = (t_start, t_end, d_start, d_end, cam_mode) => {
        fetch(`http://10.0.0.230:5000/count_vertical_camera`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                time_params: {
                    start_time: this.formatTime(t_start),
                    end_time: this.formatTime(t_end),
                    start_date: this.formatDate(d_start),
                    end_date: this.formatDate(d_end)
                },
                camera_id: cam_mode
            })
        })
            .then(response => {
                console.log(response);
                return response.json()})
            .then(data => {
                const res = data
                const datas = []
                const len = data.days.length

                for (let i = 0; i < len; i++) {
                    datas.push({
                        index: i + 1,
                        date: res.days[i],
                        start: res.start_times[i],
                        end: res.end_times[i],
                        count: res.counts[i]
                    })
                }
                this.setState({
                    data: datas,
                    header: [
                        { label: "No.", key: "index" },
                        { label: "Date", key: "date" },
                        { label: "Start time", key: "start" },
                        { label: "End time", key: "end" },
                        { label: "Count", key: "count" }
                    ]
                })

            })
            .catch(error => console.log(error))
    }

    getPeriodCSV = (t_start, t_end, d_start, d_end) => {

        fetch(`http://10.0.0.230:5000/count_vertical`, {
            mode: 'cors',
            method: "POST",
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_time: this.formatTime(t_start),
                end_time: this.formatTime(t_end),
                start_date: this.formatDate(d_start),
                end_date: this.formatDate(d_end)
            })
        })
            .then(response => {
                // console.log(response);
                return response.json()
            })
            .then(data => {
                console.log(data);
                const res = data.results
                const datas = []
                const len = res.days.length
                for (let i = 0; i < len; i++) {
                    datas.push({
                        index: i + 1,
                        date: res.days[i],
                        start: res.start_times[i],
                        end: res.end_times[i],
                        count: res.counts[i]
                    })
                }

                this.setState({
                    data: datas,
                    header: [
                        { label: "No.", key: "index" },
                        { label: "Date", key: "date" },
                        { label: "Start time", key: "start" },
                        { label: "End time", key: "end" },
                        { label: "Count", key: "count" }
                    ],
                    title: "Duration report by hour for customers coming to IPH" 
                })
            })
            .catch(error => console.log(error))
    }

    render() {
        return (
            <div>
                <div className="dash-title">
                    EXPORT CUSTOMERS STASTICS DURING PERIOD
                </div>
                <div className="dash-period">
                    <div className="feature-date">
                        <div className="select-cam">
                            Select camera
                            <select id="myDropdown2" onChange={() => {
                                const dropdown2 = document.getElementById("myDropdown2")
                                this.setState({
                                    cam_mode: dropdown2.value
                                })
                            }}>
                                {
                                    this.state.cam_lists.slice(0, this.state.cam_lists.length).map((item, index) => (
                                        <option value={item}>{item}</option>
                                    ))
                                }
                            </select>
                        </div>
                        <div className="time-start">
                            Time start
                            <DatePicker
                                className='date'
                                showTimeSelect
                                showTimeSelectOnly
                                minTime={new Date(0, 0, 0, 0, 0)}
                                maxTime={new Date(0, 0, 0, 23, 30)}
                                selected={this.state.time_start}
                                onChange={(date) => {
                                    console.log((date));
                                    console.log(this.formatTime(date));
                                    this.setState({
                                        time_start: date
                                    })
                                }}
                                locale='vi'
                                dateFormat="HH:mm"
                            />
                        </div>
                        <div className="time-end">
                            Time end
                            <DatePicker
                                className='date'
                                showTimeSelect
                                showTimeSelectOnly
                                minTime={new Date(0, 0, 0, 0, 0)}
                                maxTime={new Date(0, 0, 0, 23, 30)}
                                selected={this.state.time_end}
                                onChange={(date) => {
                                    this.setState({
                                        time_end: date
                                    })
                                }}
                                locale='vi'
                                dateFormat="HH:mm"
                            />
                        </div>
                        <div className="date-start">
                            Date start
                            <DatePicker
                                className='date'
                                selected={this.state.date_start}
                                onChange={(date) => {
                                    console.log((date));
                                    console.log(this.formatDate(date));
                                    this.setState({
                                        date_start: date
                                    })
                                }}
                                locale='vi'
                                dateFormat="dd/MM/yyyy"
                            />
                        </div>
                        <div className="date-end">
                            Date end
                            <DatePicker
                                className='date'
                                selected={this.state.date_end}
                                onChange={(date) => {
                                    this.setState({
                                        date_end: date
                                    })
                                }}
                                locale='vi'
                                dateFormat="dd/MM/yyyy"
                            />
                        </div>
                    </div>
                    <div className="feature-btn">
                        <button
                            className='apply-btn'
                            onClick={() => {
                                if (this.state.cam_mode === 'All') {
                                    this.getPeriodCSV(this.state.time_start, this.state.time_end, this.state.date_start, this.state.date_end)
                                }
                                else {
                                    this.getDataPeriodByCamera(this.state.time_start, this.state.time_end, this.state.date_start, this.state.date_end, this.state.cam_mode)
                                }
                            }
                            }>
                            APPLY
                        </button>
                        <CSVLink
                            data={this.state.data}
                            headers={this.state.header}
                            filename={`${this.state.cam_mode}_period_report.csv`}
                            className="export-csv-btn"
                        >
                            <button
                                className='export-btn'>
                                EXPORT
                            </button>
                        </CSVLink>
                    </div>
                </div>
            </div>
        )
    }
}
