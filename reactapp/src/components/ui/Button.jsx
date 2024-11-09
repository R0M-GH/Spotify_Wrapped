import React from 'react';

const Button = ({children, ...props}) => {
	return (
		<button
			{...props}
			className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
		>
			{children}
		</button>
	);
};

export default Button;