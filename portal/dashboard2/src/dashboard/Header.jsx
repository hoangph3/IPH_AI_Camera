import React from "react";
import "../css/header.css"
import {
    Link
} from 'react-router-dom';
export default class Header extends React.Component {

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
                        <button className="camera-btn">
                            CAMERA
                        </button>
                    </Link>
                </div>
            </div>
        )
    }
}

