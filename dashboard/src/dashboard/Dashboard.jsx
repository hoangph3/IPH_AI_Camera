import React from 'react';
import GraphComponent from './reportComponent/GraphComponent';
import ExportComponent from './reportComponent/ExportComponent';
import '../css/dashboard.css'

export default class Dashboard extends React.Component {
    render() {
        return (
            <div className='dashboard'>
                <div className='dash-upper'>
                    <GraphComponent />
                </div>
                <div className='dash-bottom'>
                    <ExportComponent />
                </div>
            </div>
        )
    }
}

