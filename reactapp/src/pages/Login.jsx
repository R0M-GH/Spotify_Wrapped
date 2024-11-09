import React from 'react';
import Card from '../components/ui/Card';
import LoginForm from '../components/forms/LoginForm';

const Login = () => {
	const handleLogin = (credentials) => {
		// django login
		console.log('Login attempt:', credentials);
	};

	return (
		<div className="min-h-screen bg-purple-900 flex items-center justify-center">
			<Card className="w-full max-w-md">
				<h2 className="text-2xl font-bold mb-4">Login to Cosmic Tunes</h2>
				<LoginForm onSubmit={handleLogin}/>
			</Card>
		</div>
	);
};

export default Login;