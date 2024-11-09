import React, {useState} from 'react';
import Button from "../ui/Button";

const LoginForm = ({onSubmit}) => {
	const [username, setUsername] = useState('');
	const [password, setPassword] = useState('');

	const handleSubmit = (e) => {
		e.preventDefault();
		onSubmit({username, password});
	};

	return (
		<form onSubmit={handleSubmit} className="space-y-4">
			<div>
				<label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
				<input
					type="text"
					id="username"
					value={username}
					onChange={(e) => setUsername(e.target.value)}
					className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
				/>
			</div>
			<div>
				<label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
				<input
					type="password"
					id="password"
					value={password}
					onChange={(e) => setPassword(e.target.value)}
					className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500"
				/>
			</div>
			<Button type="submit">Login</Button>
		</form>
	);
};

export default LoginForm;