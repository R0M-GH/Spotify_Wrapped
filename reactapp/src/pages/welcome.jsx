'use client'

import React, {useEffect, useState} from 'react'
import {motion} from 'framer-motion'
import Button from '../components/ui/button'
import Link from 'next/link'
import {Moon, Music, Sun} from 'lucide-react'

export default function Component() {
	const [theme, setTheme] = useState('dark')

	useEffect(() => {
		document.body.className = theme
	}, [theme])

	const features = [
		{
			title: 'Cosmic Song Count',
			description: 'Discover the vast expanse of your musical library'
		},
		{
			title: 'Genre Nebulas',
			description: 'Visualize your listening habits with our genre breakdown'
		},
		{
			title: 'Stellar Hits',
			description: 'Orbit around your top songs and relive your favorite moments'
		},
		{
			title: 'Constellation of Artists',
			description: 'Explore the stars that shine brightest in your musical sky'
		}
	]

	return (
		<div
			className={`min-h-screen ${theme === 'dark' ? 'bg-[#0A0B1E] text-white' : 'bg-gray-100 text-gray-900'} ${theme === 'spotify' ? 'bg-[#1DB954] text-white' : ''} relative overflow-hidden transition-colors duration-300`}>
			{/* Theme Switcher */}
			<div className="absolute top-4 right-4 z-20 flex space-x-2">
				<Button variant="outline" size="icon" onClick={() => setTheme('light')}>
					<Sun className="h-[1.2rem] w-[1.2rem]"/>
				</Button>
				<Button variant="outline" size="icon" onClick={() => setTheme('dark')}>
					<Moon className="h-[1.2rem] w-[1.2rem]"/>
				</Button>
				<Button variant="outline" size="icon" onClick={() => setTheme('spotify')}>
					<Music className="h-[1.2rem] w-[1.2rem]"/>
				</Button>
			</div>

			{/* Orbital Rings */}
			<div className="absolute inset-0 opacity-20">
				{[1, 2, 3, 4].map((i) => (
					<motion.div
						key={i}
						className="absolute rounded-full border border-current"
						style={{
							width: `${i * 25}%`,
							height: `${i * 25}%`,
							left: '50%',
							top: '50%',
						}}
						animate={{
							rotate: 360,
						}}
						transition={{
							duration: 20 + i * 5,
							repeat: Infinity,
							ease: "linear"
						}}
					/>
				))}
			</div>

			{/* Floating Planets */}
			{[1, 2, 3, 4].map((i) => (
				<motion.div
					key={`planet-${i}`}
					className="absolute w-4 h-4 rounded-full"
					style={{
						background: theme === 'spotify' ? ['#1ED760', '#1ED760', '#1ED760', '#1ED760'][i - 1] : ['#8B5CF6', '#F59E0B', '#EF4444', '#6366F1'][i - 1],
					}}
					animate={{
						x: [0, 100, 0],
						y: [0, -50, 0],
					}}
					transition={{
						duration: 10 + i * 2,
						repeat: Infinity,
						ease: "easeInOut"
					}}
				/>
			))}

			<div className="relative z-10 container mx-auto px-4 py-16 flex flex-col items-center text-center">
				<motion.h1
					className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4"
					initial={{opacity: 0, y: 20}}
					animate={{opacity: 1, y: 0}}
					transition={{duration: 0.8}}
				>
					Welcome to Cosmic Tunes
				</motion.h1>

				<motion.p
					className="text-base md:text-lg text-opacity-80 mb-8 max-w-2xl"
					initial={{opacity: 0, y: 20}}
					animate={{opacity: 1, y: 0}}
					transition={{duration: 0.8, delay: 0.2}}
				>
					Embark on a stellar journey through the universe of music with Cosmic Tunes, your interstellar
					Spotify companion
				</motion.p>

				<motion.div
					className="flex flex-col sm:flex-row gap-4 mb-16 w-full sm:w-auto"
					initial={{opacity: 0, y: 20}}
					animate={{opacity: 1, y: 0}}
					transition={{duration: 0.8, delay: 0.4}}
				>
					<Button asChild variant="default" className="w-full sm:w-auto bg-primary hover:bg-primary/90">
						<Link href="/login">Login</Link>
					</Button>
					<Button asChild variant="outline"
					        className="w-full sm:w-auto border-primary text-primary hover:bg-primary/10">
						<Link href="/create">Create</Link>
					</Button>
				</motion.div>

				<motion.h2
					className="text-2xl md:text-3xl lg:text-4xl font-bold mb-12"
					initial={{opacity: 0, y: 20}}
					animate={{opacity: 1, y: 0}}
					transition={{duration: 0.8, delay: 0.6}}
				>
					Explore Your Musical Galaxy
				</motion.h2>

				<div className="grid gap-8 max-w-3xl">
					{features.map((feature, index) => (
						<motion.div
							key={feature.title}
							className="text-center"
							initial={{opacity: 0, y: 20}}
							animate={{opacity: 1, y: 0}}
							transition={{duration: 0.8, delay: 0.8 + index * 0.2}}
						>
							<h3 className="text-xl md:text-2xl font-semibold mb-2">{feature.title}</h3>
							<p className="text-sm md:text-base text-opacity-80">{feature.description}</p>
						</motion.div>
					))}
				</div>

				<motion.div
					className="flex flex-col sm:flex-row gap-4 mt-12 w-full sm:w-auto"
					initial={{opacity: 0, y: 20}}
					animate={{opacity: 1, y: 0}}
					transition={{duration: 0.8, delay: 1.6}}
				>
					<Button asChild variant="default" className="w-full sm:w-auto bg-primary hover:bg-primary/90">
						<Link href="/login">Login</Link>
					</Button>
					<Button asChild variant="outline"
					        className="w-full sm:w-auto border-primary text-primary hover:bg-primary/10">
						<Link href="/create">Create</Link>
					</Button>
				</motion.div>
			</div>
		</div>
	)
}