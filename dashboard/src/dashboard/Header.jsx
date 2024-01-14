import React from "react";
import "../css/header.css"
import {
    Link
} from 'react-router-dom';
import {ip_address, port} from '../base/config'
export default class Header extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            url: `http://${ip_address}:${port}/cam`
        }
    }
    switchToCamera = () => {
        // let cam_id = btn.replace("C", "c")
        // console.log(cam_id);
        fetch(this.state.url, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                camera_id: `cam1`
            })
        })
            .then(response => {return response.json()})
            .then(data => {
                console.log("Switch to camera");
            })
            .catch(err => console.log(err))
    }
    render() {
        return (
            <div className="head">
                <div className="head-title">IPH AI CAMERA</div>
                <div className="head-btn">
                    <Link to="/dashboard">
                        <button className="dashboard-btn" >
                            REPORT
                        </button>
                    </Link>
                    <Link to="/camera">
                        <button className="camera-btn"
                        onClick={() => this.switchToCamera()}>
                            CAMERA
                        </button>
                    </Link>
                </div>
            </div>
        )
    }
}

