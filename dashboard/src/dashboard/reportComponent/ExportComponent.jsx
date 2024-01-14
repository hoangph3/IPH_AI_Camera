import React from 'react';
import PeriodComponent from './PeriodComponent';
import DurationComponent from './DurationComponent';
import '../../css/export.css'

export default class ExportComponent extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      form1: true
    }
  }

  showForm1 = () => {
    this.setState({
      form1: true
    })
  }

  showForm2 = () => {
    this.setState({
      form1: false
    })
  }

  render() {
    return (
      <div className="dash-feature">
        <div className='mode-block'>
          <button className='period-btn' onClick={() => this.showForm1()}>PERIOD</button>
          <button className='duration-btn' onClick={() => this.showForm2()}>DURATION</button>
        </div>
        {
          this.state.form1 ? (
            <PeriodComponent />
          ) : (
            <DurationComponent />
          )
        }
      </div>
    )
  }
}

