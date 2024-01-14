import React from 'react';
import CameraListComponent from './cameraComponent/CameraListComponent';
import '../css/camera.css'
export default class Camera extends React.Component {
    render() {
        return (
            <div className='camera'>
                <CameraListComponent />
            </div>
        )
    }
}

