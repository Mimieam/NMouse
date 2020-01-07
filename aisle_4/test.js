class Tooltip extends React.Component {

  render() {
    return <div id="tooltip">this.props.text</div>;
  }
}

class App extends React.Component {
  state = {
    text: ''
  }

  onDocumentClick = (event) => {
    if (event.target.tagName === 'BUTTON') {
      this.setState({ text: event.target.textContent })
    }
  }
  
  componentDidMount() {
    document.addEventListener('click', this.onDocumentClick)
  }
  componentWillUnmount() {
    document.removeEventListener('click', this.onDocumentClick)
  }

  render() {
    return <div>
      {this.props.children}
      <Tooltip text={this.state.text}/>
    </div>
  }
}

document.body.innerHTML = "<div id='root'></div><div id='tooltip'></div>";
const rootElement = document.getElementById("root");
ReactDOM.render(<App>
  <button id="button1">First button</button>
  <button id="button2">Second button</button>
</App>, rootElement);
document.getElementById("button2").click();
setTimeout(() => console.log(document.body.innerHTML));