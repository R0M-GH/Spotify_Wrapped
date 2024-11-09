import React from 'react'
import {motion} from 'framer-motion'
import {Play} from 'lucide-react'

export default function StellarHits() {
	const topSongs = [
		{id: 1, title: 'Cosmic Rhapsody', artist: 'Galactic Queen', plays: 1000},
		{id: 2, title: 'Stardust Serenade', artist: 'Nebula Nights', plays: 950},
		{id: 3, title: 'Interstellar Groove', artist: 'Asteroid Beats', plays: 900},
		{id: 4, title: 'Lunar Lullaby', artist: 'Moonlight Melodies', plays: 850},
		{id: 5, title: 'Solar Flare Funk', artist: 'Sun Spots', plays: 800},
	]

	return (
		<div>
			<motion.h2
				className="text-3xl md:text-4xl font-bold mb-8 text-center"
				initial={{opacity: 0, y: -20}}
				animate={{opacity: 1, y: 0}}
			>
				Stellar Hits
			</motion.h2>
			<div className="space-y-4">
				{topSongs.map((song, index) => (
					<motion.div
						key={song.id}
						className="bg-green-900/30 rounded-lg p-4 backdrop-blur-sm flex items-center"
						initial={{opacity: 0, x: -20}}
						animate={{opacity: 1, x: 0}}
						transition={{duration: 0.5, delay: index * 0.1}}
					>
						<div className="mr-4">
							<motion.button
								whileHover={{scale: 1.1}}
								whileTap={{scale: 0.9}}
								className="text-green-300 hover:text-green-100"
							>
								<Play className="h-8 w-8"/>
							</motion.button>
						</div>
						<div className="flex-grow">
							<h3 className="text-xl font-semibold">{song.title}</h3>
							<p className="text-sm text-green-200">{song.artist}</p>
						</div>
						<div className="text-right">
							<p className="text-sm text-green-300">{song.plays} plays</p>
						</div>
					</motion.div>
				))}
			</div>
		</div>
	)
}