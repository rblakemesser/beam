import React, { Component } from 'react';
import beam from './beam.svg';
import BeamPresetsMenu from './BeamPresetsMenu';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={beam} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome, Beam Daddy</h1>
        </header>
        <BeamPresetsMenu />
      </div>
    );
  }
}

export default App;
