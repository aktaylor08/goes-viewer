import './App.css';
import React, { useState, useEffect } from 'react';
import useKeypress from 'react-use-keypress';


const SatImage = (props) => {
  const url = "http://127.0.0.1:8000/img/0/" + props.x + "/" + props.y
  return <img src={url} />
}

const Display = (props) => {
  return (
    <div className="tiles">
      <div className="row">
        <SatImage x={props.x} y={props.y} />
        <SatImage x={props.x + 1} y={props.y} />
        <SatImage x={props.x + 2} y={props.y} />
        <SatImage x={props.x + 3} y={props.y} />
      </div>
      <div className="row">
        <SatImage x={props.x} y={props.y + 1} />
        <SatImage x={props.x + 1} y={props.y + 1} />
        <SatImage x={props.x + 2} y={props.y + 1} />
        <SatImage x={props.x + 3} y={props.y +1} />
      </div >
    </div>
  );
}

const changeValue = (current, offset, maxVal, modFun) => {
  console.log(current, offset)
  var newVal = current + offset
  if (newVal < 0) {
    newVal = 0
  }
  if (newVal > maxVal) {
    newVal = maxVal
  }
  modFun(newVal)
}


const ImageArea = () => {
  const [x0, setX0] = useState(0);
  const [y0, setY0] = useState(0);
  const maxX = 19
  const maxY = 11
  const left = () => { changeValue(x0, -1, maxX - 1, setX0) }
  const right = () => { changeValue(x0, 1, maxX - 1, setX0) }
  const up = () => { changeValue(y0, -1, maxY - 1, setY0) }
  const down = () => { changeValue(y0, 1, maxY - 1, setY0) }
  useKeypress(["h", "j", "k", "l"], (event) =>{
    if(event.key == "h"){
      left()
    }else if(event.key == "j"){
      down()
    }else if(event.key == "k"){
      up()
    }else if(event.key == "l"){
      right()

    }
    console.log("Woah")
  })

  return (
    <div className="App" >
      <Display x={x0} y={y0} />
      <button onClick={left}>Left</button>
      <button onClick={right}>Right</button>
      <button onClick={up}>Up</button>
      <button onClick={down}>Down</button>
    </div >
  );

}


function App() {
  return (
    <div >
      <ImageArea></ImageArea>
    </div>
  );
}

export default App;
