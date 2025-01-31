import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import MediaAgent from "../components/MediaAgent";

function App() {
  const [count, setCount] = useState(0);

  return (
    <>
      <div>
        <div>
          <a href="https://react.dev" target="_blank">
            <img src={reactLogo} className="logo react" alt="React logo" />
          </a>
        </div>
        <MediaAgent></MediaAgent>
      </div>
    </>
  );
}

export default App;
