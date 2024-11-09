'use client'

import React, {useEffect, useRef, useState} from 'react'
import {AnimatePresence, motion} from 'framer-motion'

const artists = [
	{id: 1, name: 'Galactic Queen', genre: 'Cosmic Rock', listeners: 1000000, x: 0.2, y: 0.3},
	{id: 2, name: 'Nebula Nights', genre: 'Space Jazz', listeners: 800000, x: 0.8, y: 0.2},
	{id: 3, name: 'Asteroid Beats', genre: 'Astro Hip-Hop', listeners: 750000, x: 0.5, y: 0.7},
	{id: 4, name: 'Moonlight Melodies', genre: 'Lunar Classical', listeners: 600000, x: 0.3, y: 0.8},
	{id: 5, name: 'Sun Spots', genre: 'Solar Funk', listeners: 550000, x: 0.7, y: 0.6},
]

const Star = ({x, y, size, opacity}) => (
	<div
		className="absolute rounded-full bg-white"
		style={{
			left: `${x * 100}%`,
			top: `${y * 100}%`,
			width: size,
			height: size,
			opacity: opacity,
		}}
	/>
)

const ArtistStar = ({artist, isHovered, onHover, onLeave}) => (
	<motion.div
		className="absolute cursor-pointer"
		style={{left: `${artist.x * 100}%`, top: `${artist.y * 100}%`}}
		onMouseEnter={() => onHover(artist)}
		onMouseLeave={onLeave}
		initial={{scale: 1}}
		animate={{scale: isHovered ? 1.2 : 1}}
		transition={{duration: 0.3}}
	>
		<div className={`w-3 h-3 rounded-full ${isHovered ? 'bg-purple-400' : 'bg-purple-200'}`}/>
		<AnimatePresence>
			{isHovered && (
				<motion.div
					initial={{opacity: 0, y: 10}}
					animate={{opacity: 1, y: 0}}
					exit={{opacity: 0, y: 10}}
					className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 bg-purple-900/80 backdrop-blur-md p-2 rounded-lg shadow-lg w-48"
				>
					<h3 className="text-sm font-bold mb-1">{artist.name}</h3>
					<p className="text-xs text-purple-200">{artist.genre}</p>
					<p className="text-xs text-purple-300">{artist.listeners.toLocaleString()} listeners</p>
				</motion.div>
			)}
		</AnimatePresence>
	</motion.div>
)

export default function ArtistConstellation() {
	const [hoveredArtist, setHoveredArtist] = useState(null)
	const constellationRef = useRef(null)
	const [dimensions, setDimensions] = useState({width: 0, height: 0})

	useEffect(() => {
		const updateDimensions = () => {
			if (constellationRef.current) {
				setDimensions({
					width: constellationRef.current.offsetWidth,
					height: constellationRef.current.offsetHeight,
				})
			}
		}

		updateDimensions()
		window.addEventListener('resize', updateDimensions)
		return () => window.removeEventListener('resize', updateDimensions)
	}, [])

	return (
		<div className="relative w-full h-[calc(100vh-6rem)] bg-black overflow-hidden" ref={constellationRef}>
			{/* Background stars */}
			{[...Array(200)].map((_, i) => (
				<Star
					key={i}
					x={Math.random()}
					y={Math.random()}
					size={`${Math.random() * 1.5 + 0.5}px`}
					opacity={Math.random() * 0.5 + 0.25}
				/>
			))}

			{/* Constellation lines */}
			<svg className="absolute inset-0 w-full h-full">
				{artists.map((artist, index) => {
					const nextArtist = artists[(index + 1) % artists.length]
					return (
						<motion.line
							key={artist.id}
							x1={`${artist.x * 100}%`}
							y1={`${artist.y * 100}%`}
							x2={`${nextArtist.x * 100}%`}
							y2={`${nextArtist.y * 100}%`}
							stroke="rgba(139, 92, 246, 0.2)"
							strokeWidth="1"
							initial={{pathLength: 0}}
							animate={{pathLength: 1}}
							transition={{duration: 2, ease: "easeInOut"}}
						/>
					)
				})}
			</svg>

			{/* Artist stars */}
			{artists.map((artist) => (
				<ArtistStar
					key={artist.id}
					artist={artist}
					isHovered={hoveredArtist && hoveredArtist.id === artist.id}
					onHover={setHoveredArtist}
					onLeave={() => setHoveredArtist(null)}
				/>
			))}

			{/* Constellation title */}
			<motion.h2
				className="absolute top-4 left-1/2 transform -translate-x-1/2 text-2xl font-bold text-purple-200"
				initial={{opacity: 0, y: -20}}
				animate={{opacity: 1, y: 0}}
				transition={{delay: 0.5, duration: 0.8}}
			>
				Artist Constellation
			</motion.h2>
		</div>
	)
}