import {useEffect, useState} from 'react';

const useTheme = () => {
	const [theme, setTheme] = useState('dark');

	useEffect(() => {
		document.body.className = theme;
	}, [theme]);

	const toggleTheme = () => {
		setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
	};

	return [theme, toggleTheme];
};

export default useTheme;