import React from 'react';
import {Link} from 'react-router-dom';

const Navigation = () => {
	return (
		<nav className="bg-purple-900 p-4">
			<ul className="flex space-x-4">
				<li><Link to="/" className="text-white hover:text-purple-200">Home</Link></li>
				<li><Link to="/login" className="text-white hover:text-purple-200">Login</Link></li>
				<li><Link to="/create-account" className="text-white hover:text-purple-200">Create Account</Link></li>
				<li><Link to="/cosmic-explorer" className="text-white hover:text-purple-200">Cosmic Explorer</Link></li>
			</ul>
		</nav>
	);
};

export default Navigation;