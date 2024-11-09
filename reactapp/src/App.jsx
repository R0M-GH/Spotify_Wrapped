import React from 'react';
import {BrowserRouter as Router, Route, Routes} from 'react-router-dom';
import Navigation from './components/layout/Navigation';
import Welcome from './pages/Welcome';
import Login from './pages/Login';
import CreateAccount from './pages/CreateAccount';
import CosmicTunes from './pages/CosmicTunes';
import useTheme from './hooks/theme';
import './styles/App.css';

function App() {
	const [theme, toggleTheme] = useTheme();

	return (
		<Router>
			<div className={`App ${theme}`}>
				<Navigation/>
				<button onClick={toggleTheme} className="absolute top-4 right-4 bg-purple-600 text-white p-2 rounded">
					Toggle Theme
				</button>
				<Routes>
					<Route path="/" element={<Welcome/>}/>
					<Route path="/login" element={<Login/>}/>
					<Route path="/create-account" element={<CreateAccount/>}/>
					<Route path="/cosmic-explorer" element={<CosmicTunes/>}/>
				</Routes>
			</div>
		</Router>
	);
}

export default App;