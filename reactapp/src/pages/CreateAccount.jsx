import React from 'react';
import Card from '../components/ui/Card';
import CreateAccountForm from '../components/forms/CreateAccountForm';

const CreateAccount = () => {
	const handleCreateAccount = (userData) => {
		// django call
		console.log('Create account attempt:', userData);
	};

	return (
		<div className="min-h-screen bg-purple-900 flex items-center justify-center">
			<Card className="w-full max-w-md">
				<h2 className="text-2xl font-bold mb-4">Create a Cosmic Tunes Account</h2>
				<CreateAccountForm onSubmit={handleCreateAccount}/>
			</Card>
		</div>
	);
};

export default CreateAccount;