import React from 'react'
import {motion} from 'framer-motion'

export default function GenreNebula() {
	const genres = [
		{name: 'Rock', percentage: 30},
		{name: 'Pop', percentage: 25},
		{name: 'Electronic', percentage: 20},
		{name: 'Hip Hop', percentage: 15},
		{name: 'Classical', percentage: 10},
	]

	return (
		<div>
			<motion.h2
				className="text-3xl md:text-4xl font-bold mb-8 text-center"
				initial={{opacity: 0, y: -20}}
				animate={{opacity: 1, y: 0}}
			>
				Genre Nebula
			</motion.h2>
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{genres.map((genre, index) => (
					<motion.div
						key={genre.name}
						className="bg-orange-900/30 rounded-lg p-4 backdrop-blur-sm"
						initial={{opacity: 0, scale: 0.8}}
						animate={{opacity: 1, scale: 1}}
						transition={{duration: 0.5, delay: index * 0.1}}
					>
						<h3 className="text-xl font-semibold mb-2">{genre.name}</h3>
						<div className="relative h-4 bg-orange-200/20 rounded-full overflow-hidden">
							<motion.div
								className="absolute top-0 left-0 h-full bg-orange-400"
								initial={{width: 0}}
								animate={{width: `${genre.percentage}%`}}
								transition={{duration: 1, delay: 0.5 + index * 0.1}}
							/>
						</div>
						<p className="mt-2 text-right text-orange-200">{genre.percentage}%</p>
					</motion.div>
				))}
			</div>
		</div>
	)
}