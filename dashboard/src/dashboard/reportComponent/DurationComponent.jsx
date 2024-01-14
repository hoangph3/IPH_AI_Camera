import React from 'react';
import DatePicker from "react-datepicker";
import { registerLocale, setDefaultLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { ip_address } from "../../base/config"
import { CSVLink } from 'react-csv';
import vi from 'date-fns/locale/vi';
registerLocale('vi', vi)
setDefaultLocale('vi');

export default class DurationComponent extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            time_start: "",
            time_end: "",
            date_start: "",
            date_end: "",
            mode: "hour",
            hour: true,
            data: [],
            header: [],
            cam_mode: "All",
            title: "Duration report by hour for customers coming to IPH",
            cam_lists: ["All", "Cam1", "Cam2", "Cam3", "Cam4", "Cam5", "Cam6", "Cam7",
                "Cam8", "Cam9", "Cam10", "Cam11", "Cam12", "Cam13", "Cam14",
                "Cam15", "Cam16", "Cam17", "Cam18", "Cam19", "Cam20", "Cam21"]
        }
    }

    formatTime = (dateString) => {
        const date = new Date(dateString)
        // return dateString.substr(16, 5)
        return date.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit', hour12:false})
    }

    formatDate = (dateString) => {
        const date = new Date(dateString)
        const x = date.toLocaleDateString([], {day:'2-digit', month:'2-digit', year:'numeric'}).toString();
        const parts = x.split('/');
        return `${parts[1]}/${parts[0]}/${parts[2]}`
        // return date.toLocaleDateString([], {day:'2-digit', month:'2-digit', year:'numeric'})
    }

    getDataDurationByCamera = (t_start, t_end, d_start, d_end, mode, cam_mode) => {
        fetch(`http://10.0.7.88:5000/count_horizontal_v2`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start_time: `${this.formatTime(t_start)} ${this.formatDate(d_start)}`,
                end_time: `${this.formatTime(t_end)} ${this.formatDate(d_end)}`,
                mode: mode,
                camera_id: cam_mode,
            })
        })
            .then(response => {
                return response.json()
            })
            .then(data => {
                console.log(data);
                const datas = []
                const len = data.counts.length
                if (mode === "hour") {
                    for (let i = 0; i < len; i++) {
                        datas.push({
                            index: i + 1,
                            date: data.days[i],
                            start: data.start_times[i],
                            end: data.end_times[i],
                            count: data.counts[i]
                        })
                    }

                    datas.push({
                        index: len + 1,
                        date: "Total",
                        start: "",
                        end: "",
                        count: data.total_count_hour
                    })

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
                }
                else {
                    for (let i = 0; i < len; i++) {
                        datas.push({
                            index: i + 1,
                            date: data.days[i],
                            count: data.counts[i]
                        })
                    }

                    datas.push({
                        index: len + 1,
                        date: "Total",
                        count: data.total_count_day
                    })

                    this.setState({
                        data: datas,
                        header: [
                            { label: "No.", key: "index" },
                            { label: "Date", key: "date" },
                            { label: "Count", key: "count" }
                        ],
                        title: "Duration report by day for customers coming to IPH"
                    })
                }
            })
    }

    getDurationCSV = (t_start, t_end, d_start, d_end, mode) => {
        fetch(`http://10.0.7.88:5000/count_horizontal_v2`, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_time: `${this.formatTime(t_start)} ${this.formatDate(d_start)}`,
                end_time: `${this.formatTime(t_end)} ${this.formatDate(d_end)}`,
                mode: mode
            })
        })
            .then(response => {return response.json()})
            .then(data => {
                console.log(data);
                const datas = []
                const len = data.counts.length
                if (mode === "hour") {
                    for (let i = 0; i < len; i++) {
                        datas.push({
                            index: i + 1,
                            date: data.days[i],
                            start: data.start_times[i],
                            end: data.end_times[i],
                            count: data.counts[i]
                        })
                    }

                    datas.push({
                        index: len + 1,
                        date: "Total",
                        start: "",
                        end: "",
                        count: data.total_count_hour
                    })

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
                }
                else {
                    for (let i = 0; i < len; i++) {
                        datas.push({
                            index: i + 1,
                            date: data.days[i],
                            count: data.counts[i]
                        })
                    }

                    datas.push({
                        index: len + 1,
                        date: "Total",
                        count: data.total_count_day
                    })

                    this.setState({
                        data: datas,
                        header: [
                            { label: "No.", key: "index" },
                            { label: "Date", key: "date" },
                            { label: "Count", key: "count" }
                        ],
                        title: "Duration report by day for customers coming to IPH"
                    })
                }
            })
            .catch(error => console.log(error))
    }

    render() {
        return (
            <div>
                <div className="dash-title">
                    EXPORT CUSTOMERS STASTICS DURING DURATION
                </div>
                <div className="dash-duration">
                    <div className="feature-date">
                        <div className="select-mode">
                            Select mode
                            <select id="myDropdown1" onChange={() => {
                                const dropdown1 = document.getElementById("myDropdown1")
                                this.setState({
                                    mode: dropdown1.value
                                })
                            }}>
                                <option value="hour">Hour</option>
                                <option value="day">Day</option>
                            </select>
                        </div>
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
                                    this.setState({
                                        time_start: date
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
                                    this.setState({
                                        date_start: date
                                    })
                                }}
                                locale='vi'
                                dateFormat="dd/MM/yyyy"
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
                            onClick={() => {
                                if (this.state.cam_mode === "All") {
                                    console.log(this.state.cam_mode);
                                    this.getDurationCSV(this.state.time_start, this.state.time_end, this.state.date_start, this.state.date_end, this.state.mode)
                                }
                                else {
                                    this.getDataDurationByCamera(this.state.time_start, this.state.time_end, this.state.date_start, this.state.date_end, this.state.mode, this.state.cam_mode)
                                }
                            }}>
                            APPLY
                        </button>
                        <CSVLink
                            data={this.state.data}
                            headers={this.state.header}
                            filename={`${this.state.cam_mode}_duration_export.csv`}
                            className="export-csv-btn"
                        >
                            <button>EXPORT</button>
                        </CSVLink>
                    </div>
                </div >
            </div>
        )
    }
}
