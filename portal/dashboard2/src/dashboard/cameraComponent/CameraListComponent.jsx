import React from "react";
import '../../css/camera.css'
import { ip_address } from "../../base/config";

export default class CameraListComponent extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            url: `http://10.0.0.230:3030/cam1`,
            list: ['Cam1', 'Cam2', 'Cam3', 'Cam4', 'Cam5', 'Cam6', 'Cam7', 'Cam8', 'Cam9',
                'Cam10', 'Cam11', 'Cam12', 'Cam13', 'Cam14', 'Cam15', 'Cam16', 'Cam17', 'Cam18', 'Cam19',
                'Cam20', 'Cam21']
        }
    }

    getCamUrl = (btn) => {
        switch (btn) {
            case "Cam1":
                this.setState({
                    url: `http://10.0.0.230:3030/cam1`
                })
                break;
            case "Cam2":
                this.setState({
                    url: `http://10.0.0.230:3030/cam2`
                })
                break;
            case "Cam3":
                this.setState({
                    url: `http://10.0.0.230:3030/cam3`
                })
                break;
            case "Cam4":
                this.setState({
                    url: `http://10.0.0.230:3030/cam4`
                })
                break;
            case "Cam5":
                this.setState({
                    url: `http://${ip_address}:3030/cam5`
                })
                break;
            case "Cam6":
                this.setState({
                    url: `http://${ip_address}:3030/cam6`
                })
                break;
            case "Cam7":
                this.setState({
                    url: `http://${ip_address}:3030/cam7`
                })
                break;
            case "Cam8":
                this.setState({
                    url: `http://${ip_address}:3030/cam8`
                })
                break;
            case "Cam9":
                this.setState({
                    url: `http://${ip_address}:3030/cam9`
                })
                break;
            case "Cam10":
                this.setState({
                    url: `http://${ip_address}:3030/cam10`
                })
                break;
            case "Cam11":
                this.setState({
                    url: `http://${ip_address}:3030/cam11`
                })
                break;
            case "Cam12":
                this.setState({
                    url: `http://${ip_address}:3030/cam12`
                })
                break;
            case "Cam13":
                this.setState({
                    url: `http://${ip_address}:3030/cam13`
                })
                break;
            case "Cam14":
                this.setState({
                    url: `http://${ip_address}:3030/cam14`
                })
                break;
            case "Cam15":
                this.setState({
                    url: `http://${ip_address}:3030/cam15`
                })
                break;
            case "Cam16":
                this.setState({
                    url: `http://${ip_address}:3030/cam16`
                })
                break;
            case "Cam17":
                this.setState({
                    url: `http://${ip_address}:3030/cam17`
                })
                break;
            case "Cam18":
                this.setState({
                    url: `http://${ip_address}:3030/cam18`
                })
                break;
            case "Cam19":
                this.setState({
                    url: `http://${ip_address}:3030/cam19`
                })
                break;
            case "Cam20":
                this.setState({
                    url: `http://${ip_address}:3030/cam20`
                })
                break;
            case "Cam21":
                this.setState({
                    url: `http://${ip_address}:3030/cam21`
                })
                break;
            default:
                this.setState({
                    url: `http://${ip_address}:3030/cam1`
                })
        }
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
                                    // src={require(`./camera/Cam1.jpg`)}
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
