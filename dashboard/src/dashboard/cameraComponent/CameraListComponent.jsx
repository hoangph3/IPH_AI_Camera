import React from "react";
import '../../css/camera.css';
import { ip_address, port,port1,port2,port3,port4,port5,port6,
    port7,port8,port9,port10,port11,port12,port13,port14,
    port15,port16,port17,port18,port19,port20,port21 } 
from "../../base/config";

export default class CameraListComponent extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            url: `http://${ip_address}:${port}/cam`,
            list: ['Cam1', 'Cam2', 'Cam3', 'Cam4', 'Cam5', 'Cam6', 'Cam7', 'Cam8', 'Cam9',
                'Cam10', 'Cam11', 'Cam12', 'Cam13', 'Cam14', 'Cam15', 'Cam16', 'Cam17', 'Cam18', 'Cam19',
                'Cam20', 'Cam21'],
            event: ['image1', 'image2', 'image3', 'image4','image5','imag6','image7','image8','image9','image10',
            'image11', 'image12', 'image13', 'image14','image15','image16','image17','image18','image19','image20','image21']
        }
    }

    getCamUrl = (btn) => {
        let cam_id = btn.replace("C", "c")
        console.log(cam_id);
        fetch(this.state.url, {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                camera_id: `${cam_id}`
            })
        })
            .then(response => {return response.json()})
            .then(data => {
                console.log("Change button success");
            })
            .catch(err => console.log(err))
        }

    render() {
        return (
            <div>
                <div className="list-btn">
                    {
                        this.state.list.slice(0, this.state.list.length).map((item, index) => (
                            <div className="cam-btn">
                                <img
                                    src={require(`./new/new_${item}.jpg`)}
                                    onClick={async() => {
                                        await this.getCamUrl(item);
                                        console.log(this.state.url);
                                    }}
                                    alt={item} />
                                {item}
                            </div>
                        ))
                    }
                </div>
                <div className="cam-view">
                    <iframe
                        src={this.state.url}
                        title="Camera View"
                        width="100%"
                        height="660px"
                    />
                </div>
            </div>
        )
    }
}
